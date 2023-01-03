from django.conf import settings
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.filters import IngredientsFilter, RecipesFilter
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.permissions import IsAuthorOrAdminOrReadOnly
from recipes.serializers import (FavoriteSerializer, IngredientsSerializer,
                                 RecipeCreateSerializer, RecipeReadSerializer,
                                 ShoppingCartSerializer, TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipesFilter
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer
    
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_cart = 'Список покупок:'
        for ingredient in ingredients:
            shopping_cart += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response        
    
    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок и удаление рецепта из него."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {
                'user': user.id,
                'recipe': recipe.id,
            }
            serializer = ShoppingCartSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe_to_del = ShoppingCart.objects.filter(
            user=request.user, recipe=recipe)
        if not recipe_to_del:
            return Response(settings.SHOPPING_CART_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST)
        recipe_to_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """Добавление рецепта в избранное и удаление рецепта из него."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            data = {
                'user': user.id,
                'recipe': recipe.id,
            }
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        recipe_to_del = Favorite.objects.filter(
            user=request.user, recipe=recipe)
        if not recipe_to_del:
            return Response(settings.FAVORITE_ERROR_MESSAGE, status=status.HTTP_400_BAD_REQUEST)
        recipe_to_del.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    search_fields = ('^name', )
    filter_backends = (IngredientsFilter, )
