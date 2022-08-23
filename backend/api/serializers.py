from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag,
)
from users.models import Subscribe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False

        return user.subscriber.filter(author=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Ingredients


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsAmount


class SimpleRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class SubscribeSerializer(UserSerializer):
    recipes_count = serializers.IntegerField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get(
            'request').query_params.get('recipes_limit')
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                if recipes_limit < 0:
                    raise ValueError
            except ValueError:
                message = 'Параметр recipes_limit должен быть числом больше 0'
                raise serializers.ValidationError(message)

        serializer = SimpleRecipeSerializer(
            obj.recipe.all()[:recipes_limit],
            many=True,
        )

        return serializer.data


class SubscribeCreateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = '__all__'
        validators = (
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'author')
            ),
        )

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        return data


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='ingredientsamount_set',
    )
    image = serializers.SerializerMethodField('get_image_url')
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = '__all__'
        # exclude = ('publication_date',)

    def get_image_url(self, obj):
        return obj.image.url


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        import base64

        from django.core.files.base import ContentFile
        from django.utils.crypto import get_random_string
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        name = get_random_string(22) + '.' + ext

        data = ContentFile(
            base64.b64decode(imgstr),
            name=name,
        )
        return data


class IngredientsAmountSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Ingredients.objects.all()
    )

    class Meta:
        fields = ('id', 'amount')
        model = IngredientsAmount


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientsAmountSerializer(
        many=True,
    )
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='id',
        queryset=Tag.objects.all()
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        extra_kwargs = {field: {'required': True} for field in fields}


class FavoriteAndCartSerializerMixin(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )

    def to_representation(self, instance):
        serializer = SimpleRecipeSerializer(
            instance.get('recipes'),
        )

        return serializer.data


class FavoriteSerializer(FavoriteAndCartSerializerMixin):

    class Meta:
        fields = '__all__'
        model = Favorite


class CartSerializer(FavoriteAndCartSerializerMixin):

    class Meta:
        model = Cart
        fields = '__all__'
