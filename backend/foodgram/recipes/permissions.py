from django.conf import settings
from rest_framework import permissions


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    """Ограничение доступа редактирования или удаления."""
    message = settings.IS_AUTHOR_OR_ADMIN_ERROR_MESSAGE

    def has_permission(self, request, view):
        # вернула удаленный на первом ревью метод
        # без него все падает при попытке без токена создать рецепт
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
            or request.user == obj.author
        )
