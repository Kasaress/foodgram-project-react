from recipes.models import Tag, Recipe, Ingredient, IngredientRecipe
from rest_framework import serializers
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        
          
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
    
        
class IngredientRecipetSerializer(serializers.ModelSerializer):
    name = IngredientSerializer()
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount') 
        
                
class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )
        
    def get_tags(self, obj):
        return TagSerializer(
            Tag.objects.filter(recipes=obj),
            many=True,).data
        
    def get_ingredients(self, obj):
        return IngredientRecipetSerializer(
            Ingredient.objects.filter(recipes=obj),
            many=True,).data
        
        
class RecipeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )