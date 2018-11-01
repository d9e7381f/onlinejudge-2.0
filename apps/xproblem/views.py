from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from rest_framework import decorators, exceptions

from . import serializers, filters, docs
from .permissions import ProblemPermission
from problem.models import Problem
from apps.utils import permissions
from apps.utils.response import Response
from apps.utils.views import GetSerializerClass, MyModelViewSet
from apps.xproblem.models import ProblemValidation
from apps.comment.serializers import CommentSerializer
from apps.delegation.models import Delegation
from contest.models import Contest
from apps.contest.utils import is_competitor

User = get_user_model()


class ProblemViewSet(GetSerializerClass, MyModelViewSet):
    __doc__ = docs.problem_viewset
    queryset = Problem.objects.select_related('created_by__userprofile') \
                              .order_by('pk')
    serializer_class = serializers.XProblemSerializer
    filter_class = filters.ProblemFilter
    permission_classes = (ProblemPermission,)
    serializer_action_classes = {
        'list': serializers.XProblemSerializer,
        'retrieve': serializers.XProblemRetrieveSerializer,
        'create': serializers.XProblemCreateSerializer,
        'update': serializers.XProblemUpdateSerializer,
        'vote': serializers.XProblemVoteSerializer,
        'add_to_contest': serializers.XProblemAddToContestSerializer,
        'pick_one': serializers.XProblemRetrieveSerializer,
        'comment': serializers.XProblemCommentSerializer,
        'comments': CommentSerializer,
        'partial_update': serializers.ProblemPartialUpdateSerializer,
        'my_delegation': serializers.XProblemSerializer,
        'move_public': serializers.MoveProblemPublicSerializer,
        'batch_move_public': serializers.BatchMoveProblemsPublicSerializer,
    }

    def get_queryset(self):
        """Student user can only retrieve public problem."""
        user = self.request.user

        if user.is_anonymous:
            # Anonymous can't access contest problems.
            return self.queryset.filter(
                visible=True, courses=None, contest=None)
        elif not user.is_admin_role():
            request = self.request
            user = request.user
            # Regular user can access contest problems, if the user can
            # attend the contest.
            contests = [
                each for each in Contest.objects.filter(
                    start_time__lte=timezone.now()
                ) if is_competitor(each, user, request)
            ]

            return self.queryset.filter(
                Q(visible=True), \
                Q(contest=None, courses=None)
                | Q(contest__in=contests)
                | Q(created_by=user, is_valid=False))
        else:
            # Admin can access all problems.
            return self.queryset

    @decorators.list_route(methods=('GET',),
                           permission_classes=(permissions.IsAuthenticated,))
    def can_create(self, request, *args, **kwargs):
        """Whether a user can create a problem.

        Regular user can only create a problem if she haven't run out
        of her invalid problems quota.

        Since problems created by admin user are valid already, admin
        user can always create a problem.
        """
        user = request.user
        if user.problem_set.filter(is_valid=False).count() \
           >= settings.INVALID_PROBLEMS_QUOTA:
            msg = '你的题目贡献配额已满, 需之前贡献的题目通过审核后, 方能再次提交.'
            raise exceptions.ValidationError(msg)
        else:
            return Response('Success')

    @decorators.detail_route(methods=('POST',),
                             permission_classes=(permissions.IsAuthenticated,))
    def vote(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.update_vote_rank_score()
        return Response('Success')

    @decorators.detail_route(methods=('PUT',),
                             permission_classes=(permissions.IsAdmin,))
    def validate(self, request, *args, **kwargs):
        """Validate problem by admin."""
        user = request.user
        instance = self.get_object()

        # For delegation problem, only the delegator of it can validate
        # the problem.
        if instance.courses \
           and not user.delegations.filter(course=instance.courses.first()):
            raise exceptions.PermissionDenied('非法操作')

        ProblemValidation.objects.update_or_create(problem=instance, user=user)
        instance.is_valid = True
        instance.save()

        return Response('Success')

    @decorators.list_route(methods=('POST',),
                           permission_classes=(permissions.IsAdmin,))
    def add_to_contest(self, request, *args, **kwargs):
        """Add a problem to a contest."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Success')

    @decorators.list_route(methods=('GET',))
    def pick_one(self, request):
        """Pick a random problem."""
        # As frontend request, this API only return pk rather than
        # problem data.
        pk = self.get_queryset().order_by('?').first().pk
        return Response(pk)

    @decorators.detail_route(methods=('GET',),
                             permission_classes=(permissions.IsAuthenticated,))
    def comments(self, request, *args, **kwargs):
        """List comments of a problem."""
        queryset = self.get_object().comments.all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @decorators.detail_route(methods=('POST',),
                             permission_classes=(permissions.IsAuthenticated,))
    def comment(self, request, *args, **kwargs):
        """Post a comment to a problem."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Success')

    @decorators.list_route(methods=('GET',),
                           permission_classes=(permissions.IsAdmin,))
    def my_delegation(self, request, *args, **kwargs):
        """Course problems created by my delegates."""
        user = request.user
        delegations = Delegation.objects.filter(delegator=user)
        # Courses the current user choose for delegates.
        courses = [each.course for each in delegations]

        # Delegates of the current user.
        delegates = User.objects.none()
        for each in delegations:
            delegates |= each.delegates.all()

        queryset = self.filter_queryset(self.get_queryset()) \
                       .exclude(courses=None) \
                       .filter(courses__in=courses,
                               created_by__in=delegates)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Success')

    @decorators.detail_route(methods=('POST',),
                             permission_classes=(permissions.IsAdmin,))
    def move_public(self, request, *args, **kwargs):
        """
        Move a course problem to public problem set with a collection
        you choose.
        """
        instance = self.get_object()
        # Only course problem can perform this function.
        if not instance.courses.exists():
            msg = 'Only course problem can perform this function.'
            raise exceptions.ValidationError(msg)

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Success')

    @decorators.list_route(methods=('POST',),
                           permission_classes=(permissions.IsAdmin,))
    def batch_move_public(self, request, *args, **kwargs):
        """
        Move all problems of a course to public problem set with a
        default collection you choose.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Success')
