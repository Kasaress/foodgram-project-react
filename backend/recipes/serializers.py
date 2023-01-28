from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Follow, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from users.models import CustomUser as User
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов в рецептах."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingrs_recipes'
    )
    image = Base64ImageField(max_length=None)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'is_favorited', 'is_in_shopping_cart',
            'image', 'text', 'cooking_time'
        )

    def _is_exist(self, arg0, obj):
        """Возвращает информацию о существовании объекта."""
        request = self.context.get('request', None)
        if request:
            current_user = request.user
            return arg0.objects.filter(
                user=current_user.id,
                recipe=obj.id
            ).exists()
        return None

    def get_is_in_shopping_cart(self, obj):
        """Возвращает присутствие рецепта в списке покупок."""
        return self._is_exist(ShoppingCart, obj)

    def get_is_favorited(self, obj):
        """Возвращает присутствие рецепта в избранном."""
        return self._is_exist(Favorite, obj)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True,
    )
    image = Base64ImageField(max_length=None)
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'cooking_time'
        )

    @staticmethod
    def set_recipe_ingredient(ingredients, recipe):
        """Добавляет ингредиенты в рецепт."""
        ingredient_list = [
            IngredientRecipe(
                ingredient=get_object_or_404(
                    Ingredient, pk=ingredient.get('id').id
                ),
                recipe=recipe,
                amount=ingredient.get('amount'),
             )
            for ingredient in ingredients
        ]
        ingredient_list.sort(key=(lambda item: item.ingredient.name))
        IngredientRecipe.objects.bulk_create(ingredient_list)

    def create(self, validated_data):
        """Сохраняет рецепт в БД и возвращает его."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
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
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        self.set_recipe_ingredient(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод для отображения данных в соответствии с ТЗ."""
        return RecipeReadSerializer(instance).data


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
        queryset = obj.author.recipes.all()
        request = self.context.get('request')
        if request:
            limit = request.query_params.get('recipes_limit')
            if limit:
                queryset = queryset[: int(limit)]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class SubscribeSerializer(CustomUserSerializer):
    """Сериализатор для подписки на автора и отписки от него."""

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
        return SubscriptionsSerializer(instance).data
