from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """
    GET, POST, PATCH, PUT, DELETE - admin.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_staff)


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    GET - доступно всем
    POST, PATCH, PUT, DELETE - only admin.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin)


class AdminModeratorAuthorPermission(permissions.BasePermission):
    """
    GET - доступно всем
    POST, PATCH, PUT, DELETE - author, moderator, admin.
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (obj.author == request.user
                     or request.user.is_moderator
                     or request.user.is_admin))
