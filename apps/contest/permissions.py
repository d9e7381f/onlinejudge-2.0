from django.core.urlresolvers import resolve

from rest_framework import permissions
from rest_framework.permissions import *

from contest.models import Contest


class ContestPermission(permissions.BasePermission):
    """Permission of contest."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        actions = resolve(request.META['PATH_INFO']).func.actions
        pk = resolve(request.META['PATH_INFO']).kwargs.get('pk')
        request_method = request.method.lower()
        try:
            action = actions[request_method]
        except KeyError:
            return False
        user = request.user

        if user.is_anonymous:
            return False
        else:
            # Only creator of contest can change it.
            if pk:
                instance = Contest.objects.get(pk=pk)
                if instance.created_by != user:
                    self.message = '你不是该竞赛的创建人, 无法修改此竞赛'
                    return False

            return user.is_admin_role()
