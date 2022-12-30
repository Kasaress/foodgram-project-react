from rest_framework import permissions

class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    message = 'Изменять и удалять рецепт может только его автор и администратор.'
    
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # print(f'request.user: {request.user}')
        # print(f'obj.author: {obj.author}')
        return (
            request.method in permissions.SAFE_METHODS
            # or request.user.is_admin
            or request.user == obj.author
        )