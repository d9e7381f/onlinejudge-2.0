from collections import OrderedDict

import requests

from django.contrib import auth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from rest_framework import decorators, exceptions, mixins, permissions
from rest_framework.viewsets import GenericViewSet

from . import serializers
from .models import Group
from account.models import UserProfile
from apps.utils.response import Response
from apps.utils.views import GetSerializerClass, MyModelViewSet


User = get_user_model()


@decorators.api_view(('GET',))
def dgut_login(request):
    """Login of DGUT."""
    token = request.query_params.get('token')
    # Token is required.
    if not token:
        raise exceptions.ValidationError(settings.DGUT_LOGIN)
    else:
        # Check token and gain access token.
        data = {
            'token': token,
            'userip': request.ip,
            'appid': settings.APP_ID,
            'appsecret': settings.DGUT_APP_SECRET,
        }
        result = requests.post(settings.DGUT_CHECK_TOKEN, data=data).json()
        if result.get('error'):
            raise exceptions.ValidationError(settings.DGUT_LOGIN)
        else:
            # Get username and try to login.
            data = {
                'access_token': result.get('access_token'),
                'openid': result.get('openid'),
            }
            result = requests.post(settings.DGUT_USER_INFO, data=data).json()
            user = User.objects.filter(username=result.get('username')).first()
            if not user:
                raise exceptions.ValidationError(settings.DGUT_LOGIN)
            else:
                auth.login(request, user)
                return Response('Success')


@decorators.api_view(('GET',))
def dgut_logout(request):
    """Logout of DGUT."""
    auth.logout(request)
    return Response(settings.DGUT_LOGOUT)


@decorators.api_view(['GET', 'POST'])
def login(request, format=None):
    """
Login and get the session.

    POST /api/xlogin/
    {
      "username": <username>,
      "password": <password>
    }
"""
    try:
        username = request.data['username']
        password = request.data['password']
    except KeyError:
        raise exceptions.ValidationError('请输入用户名和密码')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise exceptions.ValidationError('用户名不存在')
    if not user.is_active:
        raise exceptions.ValidationError('账户已失效')
    if not user.check_password(password):
        raise exceptions.ValidationError('密码错误')

    auth.login(request, user)
    return Response('Success')


class UserViewSet(GetSerializerClass,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    """
# User List

Filter by grade: `GET /user/?userprofile__group__grade=<grade>`

Filter by major: `GET /user/?userprofile__group__major=<major>`

Filter by class number: `GET /user/?userprofile__group__class_num=<class_num>`

All the filters can be combined.

---
# User Rank
Get user rank with problem count and vote count.

    GET /user/rank/

`problem_count`: number of valid problems user create.

`vote_count`: number of up votes user receive from her created problem.

For contribution rank, change order in filter with query param.
"""
    queryset = User.objects.filter(admin_type='Regular User') \
                           .select_related('userprofile__group')
    serializer_class = serializers.UserRankSerializer
    permission_classes = (permissions.IsAuthenticated,)
    serializer_action_classes = {
        'list': serializers.UserMinSerializer,
    }
    filter_fields = (
        'username',
        'userprofile__group__grade',
        'userprofile__group__major',
        'userprofile__group__class_num',
    )

    def get_queryset_list(self, clause):
        """Get users data and their problem_count and vote_count.

        problem_count: number of problems the user created.
        vote_count: number of up votes received from problems the user
                    created.
        """
        sql = """
SELECT a.*, b.vote_count, c.*
  FROM (SELECT u.*,
               COUNT(p.id) AS problem_count
          FROM problem AS p
         RIGHT JOIN "user" AS u
            ON u.id = p.created_by_id
          LEFT JOIN collection_course_problems cp
            ON p.id = cp.problem_id
         WHERE cp.course_id IS NULL
           AND p.contest_id IS NULL
           AND p.is_valid = TRUE
         GROUP BY u.id) AS a
  LEFT JOIN (SELECT u.*,
                    COUNT(v.id) AS vote_count
               FROM problem AS p
              RIGHT JOIN "user" AS u
                 ON u.id = p.created_by_id
               LEFT JOIN vote_vote AS v
                 ON p.id = v.problem_id
              WHERE p.contest_id IS NULL
                AND p.is_valid = TRUE
                AND v.is_up = TRUE
              GROUP BY u.id) AS b
    ON a.id = b.id
  LEFT JOIN (SELECT up.*,
                    ug.name AS "group"
               FROM user_profile AS up
               LEFT JOIN user_group AS ug
                 ON up.group_id=ug.id) AS c
    ON a.id = c.user_id
        """
        return User.objects.raw(sql + clause)[:]

    def list(self, request, *args, **kwargs):
        return Response(super().list(request, *args, **kwargs))

    @decorators.list_route(methods=('GET',))
    def rank(self, request, *args, **kwargs):
        pms = request.query_params
        clause = ''

        # Filter.
        # Only list the regular users.
        if pms.get('no_admin') == 'true':
            clause = "where a.admin_type = 'Regular User' "

        # Order.
        # Order by problem_count
        if 'order_by_problem_count_desc' in pms:
            if pms['order_by_problem_count_desc'] == 'false':
                clause += 'ORDER BY problem_count'
            else:
                clause += 'ORDER BY problem_count DESC'

        # Order by vote_count
        elif 'order_by_vote_count_desc' in pms:
            if pms['order_by_vote_count_desc'] == 'false':
                clause += 'ORDER BY vote_count'
            else:
                clause += 'ORDER BY vote_count DESC'

        # Get the queryset.
        queryset = self.get_queryset_list(clause)

        # Boilerplate from ListModelMixin.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(self.get_paginated_response(serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Get the object.
        clause = f"where a.id = {kwargs['pk']}"
        try:
            instance = self.get_queryset_list(clause)[0]
        except IndexError:
            raise exceptions.NotFound

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserProfileViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    """User profile viewset."""
    queryset = UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer


class UserDebugViewSet(GetSerializerClass, MyModelViewSet):
    """User viewset only for debug."""
    queryset = User.objects.all()
    serializer_class = serializers.UserDebugSerializer
    serializer_action_classes = {
        'create': serializers.UserDebugCreateSerializer,
        'update': serializers.UserDebugUpdateSerializer,
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Success')


class GroupViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    """
Group view set.
"""
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer

    def list(self, request, *args, **kwargs):
        """List of all groups categorized by grade and major."""
        ret = OrderedDict()
        for each in Group.objects.order_by('-grade', 'major', 'class_num'):
            grade = str(each.grade)  # grade is integer
            major = each.major

            if grade not in ret.keys():
                ret[grade] = OrderedDict()
            if major not in ret[grade]:
                ret[grade][major] = []

            ret[grade][major].append(
                serializers.GroupSerializer(
                    each, context={'request': request}).data
            )

        return Response(ret)

    def retrieve(self, request, *args, **kwargs):
        return Response(super().retrieve(request, *args, **kwargs))
