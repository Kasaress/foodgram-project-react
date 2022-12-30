from recipes.models import Tag, Recipe, Ingredient, IngredientRecipe, ShoppingCart, Favorite
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model

User = get_user_model()
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        
          
class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
    
        
class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount') 
        
                
class RecipeReadSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set', many=True)
    image = Base64ImageField(max_length=None)
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
        
        
        
class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipe_set')
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )
        
    def set_recipe_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient.popitem(last=False)[1]['id']
            ingredient_amount = ingredient.popitem(last=False)[1]
            ingredient_to_add = get_object_or_404(Ingredient, pk=ingredient_id)
            if ingredient_to_add:
                IngredientRecipe.objects.create(
                    ingredient=ingredient_to_add,
                    recipe=recipe,
                    amount=ingredient_amount
                )
        
        
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredient(ingredients, recipe)
        return recipe
    
    
    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        instance.tags.set(tags)
        self.set_recipe_ingredient(ingredients, instance)
        return super().update(instance, validated_data)
    
    
class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
            
    def validate(self, data):
        user = data['user']
        if user.shopping_card.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок'
            )
        return data
    
    
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
            
    def validate(self, data):
        user = data['user']
        if user.favorite.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже в избранном'
            )
        return data