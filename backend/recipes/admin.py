from django.contrib import admin
from django.contrib.auth.models import Group
from recipes.models import Ingredient, Recipe, Tag


class TabularInlineRecipeTag(admin.TabularInline):
    """Класс для красивого отображения тэгов в рецепте."""
    model = Recipe.tags.through
    extra = 1
    min_num = 1


class TabularInlineRecipeIngredient(admin.TabularInline):
    """Класс для красивого отображения ингредиентов в рецепте."""
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


class TagAdmin(admin.ModelAdmin):
    """Тэги с поиском по названию."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    """Ингредиенты с поиском и фильтром по названию."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )


class RecipeAdmin(admin.ModelAdmin):
    """Рецепты с поиском и фильтрами по названию, автору и тэгам."""
    list_display = (
        'name',
        'author',
        'cooking_time',
        'get_favorite',
        'get_ingredients'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (TabularInlineRecipeTag, TabularInlineRecipeIngredient)

    @admin.display(description='В избранном')
    def get_favorite(self, obj):
        return obj.favorite.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(
            f'{ingr.name} - '
            f'{obj.ingrs_recipes.filter(ingredient=ingr.id).first().amount} '
            f'{ingr.measurement_unit} '
            for ingr in obj.ingredients.all()
        )


admin.site.unregister(Group)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
