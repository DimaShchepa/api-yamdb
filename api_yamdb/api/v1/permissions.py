from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import User


class IsAdmin(BasePermission):
    """Allow access only to YaMDb administrators."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Allow reads to everyone and writes only to administrators."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """Allow object changes to its author, moderators, or administrators."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True

        if request.user.role in [User.MODERATOR, User.ADMIN]:
            return True

        return False
