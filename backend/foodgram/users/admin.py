from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Модель пользователя для админки с поиском по почте и юзернейму."""
    list_display = ('pk', 'username', 'email',
        'first_name',
        'last_name',
        'password',
        )
    search_fields = ('email', 'username',)
    ordering = ('email',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)