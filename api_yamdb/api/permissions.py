from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsAuthorModeratorAdminOrReadOnly(BasePermission):
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
    # def has_object_permission(self, request, view, obj):
    #     return (
    #         request.method in SAFE_METHODS
    #         or obj.author == request.user
    #         or request.user.is_moderator
    #         or request.user.is_admin
    #     )