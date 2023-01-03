from recipes.models import Tag, Recipe, Ingredient, IngredientRecipe, ShoppingCart, Favorite, Follow
from rest_framework import serializers
from users.serializers import CustomUserSerializer
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework import serializers, status

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
        return TagSerializer(
            Tag.objects.filter(recipes=obj),
            many=True,).data
        
    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return ShoppingCart.objects.filter(
            user=current_user.id,
            recipe=obj.id,
        ).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
        return Favorite.objects.filter(
            user=current_user.id,
            recipe=obj.id
        ).exists()
        
        
        
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
    
    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context={
                 'request': self.context.get('request')
            }).data
   
class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
             
class ShoppingCartSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        
        


class SubscriptionsSerializer(CustomUserSerializer):
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
        # print('obj', obj)
        # print('obj id', obj.id)
        queryset = Recipe.objects.filter(author=obj.author.id)
        return ShortRecipeSerializer(queryset, many=True).data


    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author.id).count()
    
    
    

class SubscribeSerializer(CustomUserSerializer):
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
        # print('instance author', type(instance['author']))
        # print('instance author id', instance['author'].id)
        follow = Follow.objects.filter(
            user=instance['user'],
            author=instance['author']
        ).first()
        return SubscriptionsSerializer(
            follow,
            context={'request': self.context.get('request')}
        ).data