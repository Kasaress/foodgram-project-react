import django_filters
from django_filters import rest_framework
from .models import Recipe, Tag, Ingredient


class RecipesFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
        )

    class Meta:
        model = Recipe
        # fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
        fields = ['author', 'tags',]