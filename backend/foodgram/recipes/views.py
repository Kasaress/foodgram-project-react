
from rest_framework import viewsets
from recipes.models import Tag, Recipe, ShoppingCart, IngredientRecipe, Favorite, Ingredient
from recipes.serializers import TagSerializer, RecipeReadSerializer, RecipeCreateSerializer, ShoppingCartSerializer, FavoriteSerializer, IngredientsSerializer
from rest_framework.decorators import action
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from recipes.permissions import IsAuthorOrAdminOrReadOnly
from recipes.filters import RecipesFilter, IngredientsFilter
from django_filters.rest_framework import DjangoFilterBackend



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None



class RecipeViewSet(viewsets.ModelViewSet):
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
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_card__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        shopping_list = 'Список покупокы:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response        
    
    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
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
        get_object_or_404(
            ShoppingCart,
            user=user.id,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['POST', 'DELETE'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
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
        get_object_or_404(
            Favorite,
            user=user.id,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None
    search_fields = ('^name', )
    filter_backends = (IngredientsFilter, )
