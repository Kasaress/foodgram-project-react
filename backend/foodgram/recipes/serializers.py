from recipes.models import Tag, Recipe, Ingredient, IngredientRecipe
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404

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
    # ingredients = IngredientSerializer(
    #     many=True,
    #     )
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )
        
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient.popitem(last=False)[1]['id']
            ingredient_amount = ingredient.popitem(last=False)[1]
            ing_to_add = get_object_or_404(Ingredient, pk=ingredient_id)
            if ing_to_add:
                IngredientRecipe.objects.create(ingredient=ing_to_add, recipe=recipe, amount=ingredient_amount)
        return recipe
    
    
    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        instance.tags.set(tags)
        for ingredient in ingredients:
            ingredient_id = ingredient.popitem(last=False)[1]['id']
            ingredient_amount = ingredient.popitem(last=False)[1]
            ingredient_to_add = get_object_or_404(Ingredient, pk=ingredient_id)
            if ingredient_to_add:
                IngredientRecipe.objects.create(ingredient=ingredient_to_add, recipe=instance, amount=ingredient_amount)
        return super().update(instance, validated_data)