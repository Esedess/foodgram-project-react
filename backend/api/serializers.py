from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag,
)
from users.models import Subscribe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed',
    )

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

        return (
            not user.is_anonymous
            and user.subscriber.filter(author=obj).exists()
        )


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
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes',
    )

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
        if recipes_limit:
            if not recipes_limit.isdigit():
                message = 'Параметр recipes_limit должен быть числом'
                raise serializers.ValidationError(message)
            recipes_limit = int(recipes_limit)
            if recipes_limit < 0:
                message = 'Параметр recipes_limit должен быть больше 0'
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

    def validate(self, data):
        request = self.context.get('request')
        if data.get('user') == data.get('author'):
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        subscription_exist = Subscribe.objects.filter(**data).exists()
        if request.method == 'DELETE':
            if not subscription_exist:
                msg = 'Вы не подписаны на этого пользователя'
                raise serializers.ValidationError(msg)
        if request.method == 'POST':
            if subscription_exist:
                msg = 'Вы уже подписаны на этого пользователя'
                raise serializers.ValidationError(msg)
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
    image = serializers.SerializerMethodField(
        method_name='get_image_url',
    )
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_image_url(self, obj):
        return obj.image.url


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
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
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
            'cooking_time',
        )
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients, tags, image, name, text, cooking_time = data.values()
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Необходимо указать ингредиенты для рецепта.'
            )
        set_ingr = set()
        for ingredient in ingredients:
            ingredient = ingredient.get('id')
            if ingredient in set_ingr:
                raise serializers.ValidationError(
                    'В рецепте не может быть нескольких одинаковых '
                    'ингредиентов.'
                )
            set_ingr.add(ingredient)
        if len(tags) == 0:
            raise serializers.ValidationError('Укажите теги рецепта')

        for tag in tags:
            if tag not in Tag.objects.all():
                raise serializers.ValidationError(
                    'Такого тега не существует!'
                )
        if cooking_time <= 0:
            raise serializers.ValidationError(
                'Время приготовления не может быть 0 или меньше.'
            )
        return data

    def add_ingredients(self, instance, ingrs_data):
        for ingredients in ingrs_data:
            ingridient, amount = ingredients.values()
            through = IngredientsAmount(
                recipe=instance,
                ingredients=ingridient,
                amount=amount,
            )
            through.save()
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        return self.add_ingredients(instance, ingredients_data)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.ingredients.clear()
        self.add_ingredients(
            instance, ingredients_data
        )
        instance.save()
        return instance


class FavoriteAndCartSerializerMixin(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipes = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )

    def favorite_cart_validator(self, data, model):
        request = self.context.get('request')
        recipe = data.get('recipes')
        instanse, _ = model.objects.get_or_create(
            user=request.user)
        favorite_exist = instanse.recipes.filter(pk=recipe.pk).exists()
        if request.method == 'DELETE':
            if not favorite_exist:
                msg = 'Вы не добавляли этот рецепт'
                raise serializers.ValidationError(msg)
        if request.method == 'POST':
            if favorite_exist:
                msg = 'Этот рецепт уже добавлен'
                raise serializers.ValidationError(msg)
        return data

    def to_representation(self, instance):
        serializer = SimpleRecipeSerializer(
            instance.get('recipes'),
        )

        return serializer.data


class FavoriteSerializer(FavoriteAndCartSerializerMixin):

    class Meta:
        fields = '__all__'
        model = Favorite

    def validate(self, data):
        return self.favorite_cart_validator(data, Favorite)


class CartSerializer(FavoriteAndCartSerializerMixin):

    class Meta:
        model = Cart
        fields = '__all__'

    def validate(self, data):
        return self.favorite_cart_validator(data, Cart)
