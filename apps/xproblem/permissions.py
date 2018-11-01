from django.core.urlresolvers import resolve

from rest_framework import permissions

from .models import Problem


class ProblemPermission(permissions.BasePermission):
    """Permission of problem."""
    def has_permission(self, request, view):
        if request.method in ('HEAD', 'OPTIONS'):
            return True

        actions = resolve(request.META['PATH_INFO']).func.actions
        request_method = request.method.lower()
        try:
            action = actions[request_method]
        except KeyError:
            return False
        user = request.user

        # Actions non-login-required.
        if action in ('list','retrieve'):
            return True

        # The rest of actions is login-required.
        if user.is_anonymous:
            return False

        elif action in ('update', 'create'):
            return True
        else:
            # Other methods is for admin.
            return user.is_admin_role()
