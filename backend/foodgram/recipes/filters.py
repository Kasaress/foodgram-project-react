from django_filters.rest_framework import (FilterSet,
                                           ModelMultipleChoiceFilter,
                                           NumberFilter)
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class RecipesFilter(FilterSet):
    """Фильтр для рецептов."""
    author = NumberFilter(field_name='author__id')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = NumberFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientsFilter(SearchFilter):
    """Фильтр для игредиентов с поиском по названию."""
    search_param = 'name'
