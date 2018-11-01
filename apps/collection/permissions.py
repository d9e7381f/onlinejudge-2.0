from django.core.urlresolvers import resolve

from rest_framework import permissions


class BaseCollectionPermission(permissions.BasePermission):
    """Permission of problem."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        actions = resolve(request.META['PATH_INFO']).func.actions
        request_method = request.method.lower()
        try:
            action = actions[request_method]
        except KeyError:
            return False
        user = request.user

        if user.is_anonymous:
            return False
        # if action in ('vote', 'update', 'create'):
        #     # All login user can vote, create problem and update invalid
        #     # problem created by his own.
        #     return True
        else:
            # Other unsafe methods is for admin.
            return user.is_admin_role()
