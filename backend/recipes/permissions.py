from rest_framework import permissions


class PublicAccess(permissions.BasePermission):
    """
    Разрешение для предоставления публичного доступа к тегам.
    """

    def has_permission(self, request, view):
        return request.method == 'GET'
