from django.contrib import admin


from .models import Tag, Ingredient, Recipe, TagRecipe, IngredientRecipe

class TabularInlineRecipeTag(admin.TabularInline):
    model = Recipe.tags.through
 
 
class TabularInlineRecipeIngredient(admin.TabularInline):
    model = Recipe.ingredients.through    


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name', )
    
    
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'cooking_time', 'get_favorite')
    search_fields = ('name', 'author', 'tags')
    list_filter = ('author', 'name', 'tags')
    inlines = (TabularInlineRecipeTag, TabularInlineRecipeIngredient)
    
    def get_favorite(self, obj):
        return obj.favorite.count()
    get_favorite.short_description = 'Добавлен в избранное'
    
    
    
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)