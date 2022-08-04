from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteViewSet, IngredientsViewSet, RecipeViewSet, TagViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientsViewSet, basename='ingredients')
router_v1.register(
    r'recipes/(?P<title_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)

urlpatterns = [
    path('', include(router_v1.urls)),
]
