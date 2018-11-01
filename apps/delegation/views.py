from rest_framework import decorators

from .models import Delegation
from . import serializers
from apps.utils.views import MyModelViewSet, GetSerializerClass
from apps.utils.response import Response
from apps.utils import permissions


class DelegationViewSet(GetSerializerClass, MyModelViewSet):
    """Delegation view set.

This is the record of admin users delegate regular users to add
problems into courses.

---

Get courses which the current user should add problems into:

    GET /delegation/course_choice/

    Response:
    {
        "data": {
            "course_choice": <list_of_course_id>
        },
        "error": null
    }

Create a delegation:

    POST /
    {
        "course": <course_id>,
        "delegates": [<user1>, <user2>, ...]
    }

"""
    queryset = Delegation.objects.select_related('delegator__userprofile',
                                                 'course') \
                                 .prefetch_related('delegates__userprofile')
    serializer_class = serializers.DelegationSerializer
    permission_classes = (permissions.IsAdmin,)
    filter_fields = ('course', 'delegates', 'is_completed')
    serializer_action_classes = {
        'create': serializers.DelegationModifySerializer,
        'update': serializers.DelegationModifySerializer,
    }

    @decorators.list_route(methods=('GET',),
                           permission_classes=(permissions.IsAuthenticated,))
    def course_choice(self, request, *args, **kwargs):
        # login-required
        user = request.user
        course_choice = []
        for each in user.jobs.order_by('course').distinct('course'):
            course_choice += [i.pk for i in
                              each.course.get_descendants(include_self=True)]
        # Remove duplicates.
        course_choice = list(set(course_choice))

        return Response({
            'course_choice': course_choice,
        })
