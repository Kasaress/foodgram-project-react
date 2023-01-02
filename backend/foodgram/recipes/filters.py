import django_filters
from django_filters import rest_framework
from .models import Recipe, Tag, Ingredient
from rest_framework.filters import SearchFilter

class RecipesFilter(django_filters.FilterSet):
    author = rest_framework.NumberFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
        )
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart')

        
    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
        # fields = ['author', 'tags',]
        
    
    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorite__user=self.request.user)
        return queryset
        
        
    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return
        

class IngredientsFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)