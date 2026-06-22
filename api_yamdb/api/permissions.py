from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Allow access only to YaMDb administrators."""

    def has_permission(self, request, view):
        """Check that the authenticated user has administrator rights."""
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    """Allow reads to everyone and writes only to administrators."""

    def has_permission(self, request, view):
        """Check permissions according to request method and user role."""
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
    """Allow object changes to its author, moderators, or administrators."""

    def has_permission(self, request, view):
        """Allow reads to everyone and writes to authenticated users."""
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Check whether the user may change the requested object."""
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
