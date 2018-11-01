from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from contest.models import Contest
from . import serializers, permissions
from apps.utils.views import GetSerializerClass, MyModelViewSet
from apps.utils.response import Response


class ContestViewSet(GetSerializerClass, MyModelViewSet):
    """Viewset of contest."""
    queryset = Contest.objects.all()
    permission_classes = (permissions.ContestPermission,)
    serializer_class = serializers.ContestSerializer
    serializer_action_classes = {
        'create': serializers.ContestUpdateCreateSerializer,
        'update': serializers.ContestUpdateCreateSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        param = {}

        # For non-admin user, only public contest will be retrieved.
        if user.is_anonymous or not user.is_admin_role():
            param.update({
                'visible': True,
                'groups': None,
            })

        return Contest.objects.filter(**param)
