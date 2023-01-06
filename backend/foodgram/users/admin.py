from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Модель пользователя для админки с поиском по почте и юзернейму."""
    list_display = (
        'username',
        'pk',
        'email',
        'first_name',
        'last_name',
        'get_recipes_count',
        'get_followers_count',
        'password',
    )
    search_fields = ('email', 'username',)
    ordering = ('email',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    get_recipes_count.short_description = 'Рецепты'

    def get_followers_count(self, obj):
        return obj.user.count()
    get_followers_count.short_description = 'Подписчики'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
