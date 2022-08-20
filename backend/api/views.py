from django.contrib.auth import get_user_model
from django.db.models import Aggregate, Count, Exists, OuterRef, Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filter
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ErrorDetail, NotFound, ValidationError
from rest_framework.response import Response

from .filters import CustomSearchFilter, RecipieFilter
from .pagination import LimitPageNumberPagination
from .serializers import (
    CartSerializer, FavoriteSerializer, FollowCreateDeleteSerializer,
    FollowSerializer, IngredientsSerializer, RecipeCreateUpdateSerializer,
    RecipeSerializer, TagSerializer, UserCreateSerializer, UserSerializer,
)
from .utils import get_cart_items
from recipes.models import (
    Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag,
)
from users.models import Follow

User = get_user_model()


@api_view(['GET', ])
@permission_classes([permissions.AllowAny])
def download_shopping_cart(request):
    """
    Возвращает txt со списком покупок.
    """
    user = request.user
    recipes = Cart.objects.get(user=user).recipes.all()
    filename = user.username + '-shopping-cart.txt'
    cart_items = get_cart_items(recipes)
    response = HttpResponse(cart_items, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    def get_user(self):
        return self.request.user

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ('subscriptions', 'subscribe'):
            queryset = queryset.filter(
                following__user=self.get_user()).annotate(
                recipes_count=Count('recipe'),
            )
        return queryset

    def get_permissions(self):
        if self.action in ('create', 'list', 'reset_password', ):
            self.permission_classes = (permissions.AllowAny,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        elif self.action == 'subscriptions':
            return FollowSerializer
        elif self.action == 'subscribe':
            return FollowCreateDeleteSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        DjoserUserViewSet.perform_create(self, serializer)

    @action(['get'], detail=False)
    def me(self, request, *args, **kwargs):
        user = self.get_user()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(['post'], detail=False)
    def set_password(self, request, *args, **kwargs):
        return DjoserUserViewSet.set_password(self, request, *args, **kwargs)

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        context = {'request': request}
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, pk=None):
        context = {'request': request}
        data = {
            'user': self.get_user().pk,
            'author': (pk,),
        }
        serializer = self.get_serializer(data=data)
        if request.method == 'DELETE':
            instance = get_object_or_404(Follow, **serializer.initial_data)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # user, author = (serializer.validated_data.values())
        queryset = self.get_queryset().get(id=pk)
        instance_serializer = FollowSerializer(queryset, context=context)
        return Response(instance_serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filter.DjangoFilterBackend,)
    filterset_class = RecipieFilter
    # filter_backends = (RecipieFilter,)
    # permission_classes = (permissions.IsAuthenticated,)
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            return self.queryset
        queryset = self.queryset.annotate(
            is_favorited=Exists(
                user.favorite_set.filter(recipes=OuterRef('pk'))),
            is_in_shopping_cart=Exists(
                user.cart_set.filter(recipes=OuterRef('pk'))),
        )
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        author = self.request.user
        ingredients_amount, tags, image, name, text, cooking_time = (
            serializer.validated_data.values())

        new_recipe = Recipe.objects.create(
            author=author,
            name=name,
            image=image,
            text=text,
            cooking_time=cooking_time,
        )

        for tag in tags:
            new_recipe.tags.add(tag)

        for ingredients in ingredients_amount:
            ingridient, amount = ingredients.values()
            through = IngredientsAmount(
                recipe=new_recipe,
                ingredients=ingridient,
                amount=amount,
            )
            through.save()

        instance_serializer = RecipeSerializer(
            new_recipe, context={'request': self.request})
        return Response(instance_serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        ingredients_amount, tags, image, name, text, cooking_time = (
            serializer.validated_data.values())

        instance.image = image
        instance.name = name
        instance.text = text
        instance.cooking_time = cooking_time
        instance.ingredients.clear()
        instance.tags.clear()
        instance.save()

        for ingredients in ingredients_amount:
            ingridient, amount = ingredients.values()
            through = IngredientsAmount(
                recipe=instance,
                ingredients=ingridient,
                amount=amount,
            )
            through.save()

        for tag in tags:
            instance.tags.add(tag)

        instance_serializer = RecipeSerializer(
            instance, context={'request': self.request})
        return Response(instance_serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        instance, _ = Favorite.objects.get_or_create(user=self.request.user)

        if request.method == 'DELETE':
            if not instance.recipes.filter(pk=pk).exists():
                message = {'errors': 'Такого рецепта нет в избранном'}
                raise ValidationError(message)
            instance.recipes.remove(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if instance.recipes.filter(pk=pk).exists():
            message = {'errors': 'Такой рецепт уже есть в избранном'}
            raise ValidationError(message)
        instance.recipes.add(pk)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        serializer = CartSerializer(
            data={'recipes': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        instance, _ = Cart.objects.get_or_create(user=self.request.user)

        if request.method == 'DELETE':
            if not instance.recipes.filter(pk=pk).exists():
                message = {'errors': 'Такого рецепта нет в списке покупок'}
                raise ValidationError(message)
            instance.recipes.remove(pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

        if instance.recipes.filter(pk=pk).exists():
            message = {'errors': 'Такой рецепт уже есть в списке покупок'}
            raise ValidationError(message)
        instance.recipes.add(pk)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
