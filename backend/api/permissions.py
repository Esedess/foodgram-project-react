from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """
    Права доступа: только чтение.
    read: any
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAdminModeratorOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Права доступа: Администратор, Модератор, Автор или только чтение.
    read: any
    post: authenticated
    patch|delete: author, moderator, admin
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHOD

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (not request.user.is_anonymous and (
                request.user.is_sruff
                or obj.author == request.user))
        )
