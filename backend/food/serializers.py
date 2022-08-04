from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Favorite, Ingredients, IngredientsAmount, Recipe, Tag

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
        )


# done
class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        # fields = ('id', 'name', 'color', 'slug')
        model = Tag


# done
class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        # fields = ('id', 'name', 'measurement_unit')
        model = Ingredients


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(source='ingredients.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsAmount


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = RecipeIngredientsSerializer(many=True, source='ingredientsamount_set')

    class Meta:
        # depth = 1
        model = Recipe
        fields = '__all__'
        # fields = (
        #     'id',
        #     'tags',
        #     'author',
        #     'ingredients',
        #     'is_favorited',
        #     'is_in_shopping_cart',
        #     'name',
        #     'image',
        #     'text',
        #     'cooking_time',
        # )


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        #fields = ('user', 'recipe')
        model = Favorite
