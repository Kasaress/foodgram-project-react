from django.contrib import admin
from users.models import CustomUser


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
    ordering = ('username',)

    def get_recipes_count(self, obj):
        return obj.recipes.count()
    get_recipes_count.short_description = 'Рецепты'

    def get_followers_count(self, obj):
        return obj.user.count()
    get_followers_count.short_description = 'Подписчики'


# admin.site.unregister(CustomUser)
admin.site.register(CustomUser, UserAdmin)
