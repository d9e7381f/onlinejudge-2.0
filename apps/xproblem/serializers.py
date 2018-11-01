from django.db import connection
from django.db.models import Max
from django.utils import timezone
from django.conf import settings

from rest_framework import serializers, exceptions
from rest_framework.reverse import reverse

from submission.models import JudgeStatus
from contest.models import Contest
from problem.models import Problem, ProblemTag
from apps.collection.models import Collection, Course
from apps.xproblem.models import ProblemValidation
from apps.vote.models import Vote
from apps.user.serializers import UserProfileSerializer


class ProblemValidationSerializer(serializers.HyperlinkedModelSerializer):
    """Problem review serializer."""
    user = serializers.SerializerMethodField()

    class Meta:
        model = ProblemValidation
        fields = (
            'id', 'user', 'create_time',
        )

    def get_user(self, obj):
        return obj.user.userprofile.real_name


class XProblemSerializer(serializers.HyperlinkedModelSerializer):
    """Problem list serializer."""
    tags = serializers.SlugRelatedField(
        read_only=True, many=True, slug_field='name')
    created_by = serializers.StringRelatedField()
    vote = serializers.SerializerMethodField()
    validation = ProblemValidationSerializer()
    is_creator = serializers.SerializerMethodField()
    my_status = serializers.SerializerMethodField()
    collections = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()
    userprofile = UserProfileSerializer(source='created_by.userprofile')

    class Meta:
        model = Problem
        fields = (
            'id', 'url', '_id', 'created_by', 'title', 'description', 'tags',
            'input_description', 'output_description', 'time_limit',
            'memory_limit', 'difficulty', 'visible', 'languages', 'template',
            'samples', 'spj', 'spj_language', 'spj_code', 'spj_compile_ok',
            'test_case_id', 'test_case_score', 'rule_type', 'hint', 'source',
            'vote', 'is_open_test_case', 'is_valid', 'validation', 'is_creator',
            'submission_number', 'accepted_number', 'create_time', 'my_status',
            'collections', 'courses', 'statistic_info', 'total_score', 'userprofile',
        )

    def get_difficulty(self, obj):
        m = {
            'Low': '简单',
            'Mid': '中等',
            'High': '困难',
        }
        return m[obj.difficulty]

    def get_vote(self, obj):
        return {
            'up': obj.vote_up_count,
            'down': obj.vote_down_count,
        }

    def get_is_creator(self, obj):
        return self.context.get('request').user == obj.created_by

    def get_my_status(self, obj):
        """
        Get user solve status of public problem or contest problem.
        """
        request = self.context.get('request')
        user = request.user
        contest = Contest.objects.filter(pk=request.GET.get('contest_id', 0))

        if not user.is_authenticated:
            return None
        else:
            params = {
                'user_id': user.pk,
                # Verify if it is a contest problem.
                'contest': contest.first() if contest else None
            }
            submissions = obj.submission_set.filter(**params)

            if not submissions:
                return None
            elif submissions.filter(result=JudgeStatus.ACCEPTED):
                # Status will always be accepted since its first
                # accepted status.
                return JudgeStatus.ACCEPTED
            else:
                # Otherwise use the latest status.
                return submissions.order_by('-create_time').first().result

    # Since I will change collection as a foreign key of problem, I
    # don't write a abstract function for the following two functions.
    def get_collections(self, obj):
        """Get collection ancestors list."""
        view_name = 'collection-detail'
        request = self.context.get('request')
        instance = obj.collections.first()
        if not instance:
            return []
        else:
            return [{
                'id': each.pk,
                'name': each.name,
                'url': reverse(view_name,
                               kwargs={'pk': each.pk},
                               request=request)
                } for each in \
                instance.get_ancestors(include_self=True)]

    def get_courses(self, obj):
        """Get collection ancestors list."""
        view_name = 'course-detail'
        request = self.context.get('request')
        instances = obj.courses.all()
        if not instances:
            return []
        else:
            return [[{
                'id': each.pk,
                'name': each.name,
                'url': reverse(view_name,
                               kwargs={'pk': each.pk},
                               request=request)
                } for each in \
                instance.get_ancestors(include_self=True)] \
                for instance in instances]


class XProblemRetrieveSerializer(XProblemSerializer):
    vote_status = serializers.SerializerMethodField()

    class Meta:
        model = Problem
        fields = (
            'id', 'url', '_id', 'created_by', 'title', 'description', 'tags',
            'input_description', 'output_description', 'time_limit',
            'memory_limit', 'difficulty', 'visible', 'languages', 'template',
            'samples', 'spj', 'spj_language', 'spj_code', 'spj_compile_ok',
            'test_case_id', 'test_case_score', 'rule_type', 'hint', 'source',
            'vote', 'is_open_test_case', 'is_valid', 'validation', 'is_creator',
            'submission_number', 'accepted_number', 'create_time', 'my_status',
            'collections', 'courses', 'statistic_info', 'total_score', 'userprofile',
            'vote_status',
        )

    def get_vote_status(self, obj):
        """User vote status of a problem.

        0 means user have not voted.
        1 means user voted up.
        2 means user voted down.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return 0

        try:
            return [2, 1][user.votes.get(problem=obj).is_up]
        except Vote.DoesNotExist:
            return 0


class CreateTestCaseScoreSerializer(serializers.Serializer):
    input_name = serializers.CharField(max_length=32)
    output_name = serializers.CharField(max_length=32)
    # Cast score to integer, otherwise it will be str.
    score = serializers.IntegerField(min_value=0)


class XProblemCreateSerializer(serializers.HyperlinkedModelSerializer):
    """Problem create serializer."""
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), allow_null=True, required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    contest = serializers.PrimaryKeyRelatedField(
        queryset=Contest.objects.all(), required=False, allow_null=True)
    test_case_score = serializers.ListField(
        child=CreateTestCaseScoreSerializer(),
        allow_empty=True
    )

    class Meta:
        model = Problem
        fields = (
            'collection', 'title', 'description', 'input_description',
            'output_description', 'time_limit', 'memory_limit', 'difficulty',
            'visible', 'tags', 'languages', 'template', 'samples', 'spj',
            'spj_language', 'spj_code', 'spj_compile_ok', 'test_case_id',
            'test_case_score', 'rule_type', 'hint', 'source',
            'is_open_test_case', 'course', 'contest',
        )

    def validate(self, data):
        """Whether a user can create a problem.

        Regular user can only create a problem if she haven't run out
        of her invalid problems quota.

        Since problems created by admin user are valid already, admin
        user can always create a problem.
        """
        user = self.context['request'].user
        course = data.get('course')
        contest = data.get('contest')

        # Relugar user has no permission to create contest problem.
        if contest and not user.is_admin_role():
            msg = '你无权创建竞赛题目'
            raise exceptions.PermissionDenied(msg)

        if not course and user.problem_set.filter(is_valid=False).count() \
           >= settings.INVALID_PROBLEMS_QUOTA:
            msg = '你的题目贡献配额已满, 需之前贡献的题目通过审核后, 方能再次提交.'
            raise serializers.ValidationError(msg)

        # For regular user, only delegate to the course can create
        # problem into it.
        if course and not user.is_admin_role() \
           and course.pk not in [each.course.pk
                                    for each in user.jobs.all()]:
            msg = '你未得到更新该课程题库的授权'
            raise serializers.ValidationError(msg)

        # Auto generate display ID.
        contest = data.get('contest')
        if contest:
            data['_id'] = str(contest.problem_set.count() + 1)
        else:
            pk__max = Problem.objects.aggregate(Max('pk'))['pk__max']
            if not pk__max:
                data['_id'] = '1'
            else:
                data['_id'] = str(pk__max + 1)

        return data

    def create(self, validated_data):
        collection = validated_data.pop('collection', None)
        course = validated_data.pop('course', None)
        tags = validated_data.pop('tags', None)
        user = self.context.get('request').user
        # Problem created by student is invalid by default
        is_valid = user.is_admin_role()

        # Auto generate display ID.
        contest = validated_data.pop('contest', None)

        validated_data.update({
            'created_by': user,
            'is_valid': is_valid,
            'contest': contest,
        })

        instance = Problem.objects.create(**validated_data)

        # Contest, course and collection, these three attributes of
        # problem are mutually exclusive.
        if contest:
            pass
        elif course:
            # Add problem to courses.
            instance.courses.clear()
            instance.courses.add(course)
        elif collection:
            # Add problem to collection.
            instance.collections.add(collection)
        else:
            raise serializers.ValidationError('请选择分类')

        # Add tags to problem.
        if tags:
            instance.tags.add(*[
                ProblemTag.objects.get_or_create(name=tag_name)[0] \
                for tag_name in tags
            ])

        return instance


class XProblemUpdateSerializer(serializers.HyperlinkedModelSerializer):
    """Problem create serializer."""
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), required=False, allow_null=True)
    tags = serializers.ListField(child=serializers.CharField(), required=True)
    test_case_score = serializers.ListField(
        child=CreateTestCaseScoreSerializer(),
        allow_empty=True
    )

    class Meta:
        model = Problem
        fields = (
            'collection', '_id', 'title', 'description', 'input_description',
            'output_description', 'time_limit', 'memory_limit', 'difficulty',
            'visible', 'tags', 'languages', 'template', 'samples', 'spj',
            'spj_language', 'spj_code', 'spj_compile_ok', 'test_case_id',
            'test_case_score', 'rule_type', 'hint', 'source',
            'is_open_test_case', 'course',
        )

    def validate(self, data):
        user = self.context['request'].user
        course = data.get('course')
        contest = data.get('contest')

        # Regular user has no permission to edit contest problem.
        if contest and not user.is_admin_role():
            msg = '你无权编辑竞赛题目'
            raise exceptions.PermissionDenied(msg)

        # For regular user, only delegate to the course can create
        # problem into it.
        if course and not user.is_admin_role() \
           and course.pk not in [each.course.pk
                                    for each in user.jobs.all()]:
            msg = '你未得到更新该课程题库的授权'
            raise serializers.ValidationError(msg)

        # Display ID should be integer.
        if not data['_id'].isnumeric():
            raise serializers.ValidationError('序号应为纯数字')

        return data

    def update(self, instance, validated_data):
        collection = validated_data.pop('collection', None)
        course = validated_data.pop('course', None)
        tags = validated_data.pop('tags', None)
        user = self.context.get('request').user

        if instance.courses.exists() and not course:
            raise serializers.ValidationError('课程不可为空')

        # Regular user can't modify valid problem, which include
        # contest problem.
        if not (instance.created_by == user and not instance.is_valid
                or user.is_admin_role()):
            msg = '你没有权限修改已通过审核的题目'
            raise exceptions.PermissionDenied(msg)

        for attr, v in validated_data.items():
            setattr(instance, attr, v)

        # Contest, course and collection, these three attributes of
        # problem are mutually exclusive.
        if instance.contest:
            pass
        elif course:
            # Add problem to courses.
            instance.courses.clear()
            instance.courses.add(course)
        elif collection:
            # Add problem to collection.
            instance.collections.add(collection)
        else:
            raise serializers.ValidationError('请选择分类')

        # Change tags of problem.
        instance.tags.clear()
        if tags:
            instance.tags.add(*[
                ProblemTag.objects.get_or_create(name=tag_name)[0] \
                for tag_name in tags
            ])

        instance.save()
        return instance


class XProblemAddToContestSerializer(serializers.Serializer):
    """Serializer of add a problem to a contest."""
    contest_id = serializers.PrimaryKeyRelatedField(
        queryset=Contest.objects.all())
    problem_id = serializers.PrimaryKeyRelatedField(
        queryset=Problem.objects.all())

    def save(self):
        contest = self.validated_data['contest_id']
        problem = self.validated_data['problem_id']

        problem._id = str(contest.problem_set.count() + 1)
        problem.pk = None  # Duplicate problem.

        # Reset counter and statistic info
        problem.submission_number = 0
        problem.accepted_number = 0
        problem.statistic_info = {}

        problem.save()

        # Contest problem have no courses or collection.
        contest.problem_set.add(problem)
        for attr in ('courses', 'collection'):
            setattr(problem, attr, [])

        return


class XProblemVoteSerializer(serializers.Serializer):
    """Problem vote serializer."""
    is_up = serializers.BooleanField()  # up or down

    def update(self, instance, validated_data):
        # Vote is only for public problems.
        if instance.contest or instance.courses.exists():
            return instance

        user = self.context.get('request').user
        last_vote = instance.votes.last()
        # A user can only vote once for the same problem.
        vote, created = Vote.objects.get_or_create(
            problem=instance,
            user=user,
            defaults=validated_data
        )

        if not created:
            raise serializers.ValidationError('请不要重复投票')
        else:
            ins = [-1, 1][vote.is_up]  # increment of vote score
            if not last_vote or last_vote.is_up != vote.is_up:
                vote.score = ins
            else:
                vote.score = last_vote.score + ins
            vote.save()

        instance.vote_trigger()
        return instance


class XProblemCommentSerializer(serializers.Serializer):
    """Post comment to a problem."""
    content = serializers.CharField(max_length=1024 * 1024 * 8)

    def update(self, instance, validated_data):
        if instance.contest and instance.contest.end_time > timezone.now():
            raise serializers.ValidationError('比赛过程中禁止发布评论')

        user = self.context['request'].user
        last_ins = instance.comments.last()
        ordinal = last_ins.ordinal + 1 if last_ins else 1
        instance.comments.create(user=user, ordinal=ordinal,
                                 content=validated_data['content'])
        return instance


class MoveProblemPublicSerializer(serializers.Serializer):
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all())

    def update(self, instance, validated_data):
        collection = validated_data['collection']
        instance.courses.clear()
        instance.collections.add(collection)
        instance.save()
        return instance


class BatchMoveProblemsPublicSerializer(serializers.Serializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all())

    def save(self):
        data = self.validated_data
        collection = data['collection'].pk
        course = data['course'].pk

        with connection.cursor() as cursor:
            # Add problems into specific collection.
            cursor.execute("""
            INSERT INTO collection_collection_problems (collection_id, problem_id)
            SELECT %s, problem_id
            FROM collection_course_problems
            WHERE course_id=%s;
            """, [collection, course])

            # Remove problems from courses.
            cursor.execute("""
            DELETE FROM collection_course_problems
            WHERE course_id=%s
            """, [course])


class ProblemPartialUpdateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Problem
        fields = (
            'title', 'visible', '_id',
        )

    def update(self, instance, validated_data):
        # Public problem's display ID is read only.
        if not instance.courses.exists() and not instance.contest:
            raise serializers.ValidationError('公开题目的序号无法修改')

        return super().update(instance, validated_data)
