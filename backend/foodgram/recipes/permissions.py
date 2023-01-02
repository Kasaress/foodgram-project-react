from rest_framework import permissions

class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    message = 'Изменять и удалять рецепт может только его автор и администратор.'
    
    def has_permission(self, request, view):
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