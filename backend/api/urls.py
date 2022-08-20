from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet,
    download_shopping_cart,
)

users_router_v1 = DefaultRouter()
users_router_v1.register(
    '', UserViewSet, basename='users')

recipes_router_v1 = DefaultRouter()
recipes_router_v1.register(
    'tags', TagViewSet, basename='tags')
recipes_router_v1.register(
    'recipes', RecipeViewSet, basename='recipes')
recipes_router_v1.register(
    'ingredients', IngredientsViewSet, basename='ingredients')


urlpatterns = [
    path('users/', include(users_router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'
    ),
    path('', include(recipes_router_v1.urls)),
]
