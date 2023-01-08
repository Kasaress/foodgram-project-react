from django.conf import settings
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.filters import IngredientsFilter, RecipesFilter
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from recipes.permissions import IsAuthorOrAdminOrReadOnly
from recipes.serializers import (FavoriteSerializer, IngredientsSerializer,
                                 RecipeCreateSerializer, RecipeReadSerializer,
                                 ShoppingCartSerializer, TagSerializer)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @staticmethod
    def get_shopping_cart(ingredients):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_cart.pdf"')
        shopping_cart = canvas.Canvas(response)
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        shopping_cart.setFont('FreeSans', settings.BIG_FONT)
        shopping_cart.drawString(
            settings.PADDING_START_TEXT,
            settings.PADDING_BOTTOM_FIRST_ROW,
            "Список покупок"
        )
        page_count = 1
        step = settings.PADDING_BOTTOM_ROWS
        shopping_cart.setFont('FreeSans', settings.SMALL_FONT)
        shopping_cart.drawString(
            settings.PADDING_START_NUMBER,
            settings.PADDING_BOTTOM_FIRST_ROW,
            str(page_count)
        )
        for ingredient in ingredients:
            shopping_cart.drawString(
                settings.PADDING_START_TEXT,
                step,
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}"
            )
            if step <= settings.SIZE_BETWEEN_ROW:
                page_count += 1
                step = settings.PADDING_BOTTOM_ROWS
                shopping_cart.showPage()
                shopping_cart.setFont('FreeSans', settings.BIG_FONT)
                shopping_cart.drawString(
                    settings.PADDING_START_TEXT,
                    settings.PADDING_BOTTOM_FIRST_ROW,
                    "Список покупок"
                )
                shopping_cart.setFont('FreeSans', settings.SMALL_FONT)
                shopping_cart.drawString(
                    settings.PADDING_START_NUMBER,
                    settings.PADDING_BOTTOM_FIRST_ROW,
                    str(page_count)
                )
            else:
                step -= settings.SIZE_BETWEEN_ROW
        shopping_cart.showPage()
        shopping_cart.save()
        return response

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание файла со списком покупок."""
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        return self.get_shopping_cart(ingredients)

    @staticmethod
    def create_object(serializer_class, user, recipe):
        data = {
                'user': user.id,
                'recipe': recipe.id,
            }
        serializer = serializer_class(
            data=data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок и удаление рецепта из него."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_object(
            ShoppingCartSerializer,
            user,
            recipe
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        get_object_or_404(
            ShoppingCart,
            user=request.user.id,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное и удаление рецепта из него."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        return self.create_object(
            FavoriteSerializer,
            user,
            recipe
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        get_object_or_404(
            Favorite,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Вьюсет ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    search_fields = ('^name', )
    filter_backends = (IngredientsFilter,)
