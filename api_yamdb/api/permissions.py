from rest_framework.permissions import (
    BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS
)


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


class IsAuthorModeratorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Allow object changes to its author, moderators, or administrators."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
