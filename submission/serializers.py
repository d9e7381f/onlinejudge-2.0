from django.contrib.auth import get_user_model

from .models import Submission
from utils.api import serializers
from judge.languages import language_names
from apps.user.serializers import UserProfileSerializer


User = get_user_model()


class CreateSubmissionSerializer(serializers.Serializer):
    problem_id = serializers.IntegerField()
    language = serializers.ChoiceField(choices=language_names)
    code = serializers.CharField(max_length=20000)
    contest_id = serializers.IntegerField(required=False)
    captcha = serializers.CharField(required=False)


class ShareSubmissionSerializer(serializers.Serializer):
    id = serializers.CharField()
    shared = serializers.BooleanField()


class SubmissionModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Submission
        fields = "__all__"


# 不显示submission info的serializer, 用于ACM rule_type
class SubmissionSafeModelSerializer(serializers.ModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="_id")

    class Meta:
        model = Submission
        exclude = ("info", "contest", "ip")


class SubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SerializerMethodField()
    show_link = serializers.SerializerMethodField()
    userprofile = serializers.SerializerMethodField()

    def get_problem(self, obj):
        return {
            'id': obj.problem.pk,
            'title': obj.problem.title,
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Submission
        exclude = ("info", "contest", "code", "ip")

    def get_userprofile(self, obj):
        instance = User.objects.get(pk=obj.user_id).userprofile
        return UserProfileSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def get_show_link(self, obj):
        # 没传user或为匿名user
        if self.user is None or not self.user.is_authenticated():
            return False
        return obj.check_user_permission(self.user)
