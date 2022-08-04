from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)

from .models import Favorite, Ingredients, IngredientsAmount, Recipe, Tag
from .serializers import (
    FavoriteSerializer, IngredientsSerializer, RecipeSerializer, TagSerializer,
)


# class TagViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


# class IngredientsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    # queryset = IngredientsAmount.objects.all()
    serializer_class = RecipeSerializer
    # serializer_class = IngredientsAmountSerializer
    permission_classes = (permissions.AllowAny,)
