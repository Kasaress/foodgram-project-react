from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class TabularInlineRecipeTag(admin.TabularInline):
    """Класс для красивого отображения тэгов в рецепте."""
    model = Recipe.tags.through


class TabularInlineRecipeIngredient(admin.TabularInline):
    """Класс для красивого отображения ингредиентов в рецепте."""
    model = Recipe.ingredients.through


class TagAdmin(admin.ModelAdmin):
    """Тэги с поиском по названию."""
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    """Ингредиенты с поиском и фильтром по названию."""
    list_display = ('name', 'measurement_unit')
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

    def get_favorite(self, obj):
        return obj.favorite.count()
    get_favorite.short_description = 'В избранном'

    def get_ingredients(self, obj):
        return ', '.join(
            f'{ingredient.name}' for ingredient in obj.ingredients.all()
        )
    get_ingredients.short_description = 'Ингредиенты'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
