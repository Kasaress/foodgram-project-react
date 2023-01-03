from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from users.serializers import CustomUserSerializer

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        
          
class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
    
        
class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецептах."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount') 
        
                
class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set', many=True)
    image = Base64ImageField(max_length=None)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'is_favorited', 'is_in_shopping_cart', 'image',
            'text', 'cooking_time'
        )
        
    def get_tags(self, obj):
        """Возвращает сериализованные тэги."""
        return TagSerializer(
            Tag.objects.filter(recipes=obj),
            many=True,).data
        
    def get_is_in_shopping_cart(self, obj):
        """Возвращает булево значение о присутствии рецепта в списке покупок."""
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return ShoppingCart.objects.filter(
            user=current_user.id,
            recipe=obj.id,
        ).exists()

    def get_is_favorited(self, obj):
        """Возвращает булево значение о присутствии рецепта в избранном."""
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return Favorite.objects.filter(
            user=current_user.id,
            recipe=obj.id
        ).exists()
        
        
        
class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
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
        """Добавляет ингредиенты в рецепт."""
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
        """Сохраняет рецепт в БД и возвращает его."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredient(ingredients, recipe)
        return recipe
    
    def update(self, instance, validated_data):
        """Обновляет рецепт."""
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientrecipe_set')
        instance.tags.set(tags)
        self.set_recipe_ingredient(ingredients, instance)
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """Метод для отображения данных в соответствии с ТЗ."""
        return RecipeReadSerializer(instance, context={
                 'request': self.context.get('request')
            }).data
   
class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения короткого рецепта."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
             
class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
            
    def validate(self, data):
        user = data['user']
        if user.shopping_cart.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок'
            )
        return data
    
    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
    
    
class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""
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
    
    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
    
    
class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        
        
class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для списка подписок."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count'
        )

        
    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.author.id)
        return ShortRecipeSerializer(queryset, many=True).data


    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()
    
    
class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписки на автора и отписки от него."""
    queryset = User.objects.all()

    class Meta:
        model = Follow
        fields = ('user', 'author')


    def validate(self, data):
        user = data['user']
        author = data['author']
        if Follow.objects.filter(
            user=user,
            author=author
        ).exists():
            raise ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
    
    
    def to_representation(self, instance):
        follow = Follow.objects.filter(
            user=instance['user'],
            author=instance['author']
        ).first()
        return SubscriptionsSerializer(
            follow,
            context={'request': self.context.get('request')}
        ).data