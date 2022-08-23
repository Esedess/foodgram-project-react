from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipieFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']


class IngredientsFilter(SearchFilter):
    search_param = 'name'

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '').lower()
        params = params.replace('\x00', '')  # strip null characters
        params = params.replace(',', ' ')
        return params.split()
