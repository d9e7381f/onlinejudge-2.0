from rest_framework import permissions
from rest_framework.permissions import *


class IsAdmin(permissions.BasePermission):
    """Authorized if user is admin."""
    def has_permission(self, request, view):
        user = request.user
        return not user.is_anonymous and request.user.is_admin_role()
