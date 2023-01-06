from django.conf import settings
from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Ограничение доступа редактирования или удаления."""
    message = settings.ISAUTHORORADMIN_ERROR_MESSAGE

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user == obj.author
        )
