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
    
    
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'image', 'text', 'cooking_time')
    search_fields = ('name', 'author',)
    inlines = (TabularInlineRecipeTag, TabularInlineRecipeIngredient)
    
    
    
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)