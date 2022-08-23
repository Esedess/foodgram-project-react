from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.crypto import get_random_string

from recipes.models import (
    Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag,
)
from users.models import Subscribe

User = get_user_model()

API_GET_URLS = {
    '/api/users/': (),
    '/api/users/{}/': ('401', '404'),
    '/api/users/me/': ('401', ),
    '/api/tags/': (),
    '/api/tags/{}/': ('404'),
    '/api/recipes/': (),
    '/api/recipes/{}/': (),
    '/api/recipes/download_shopping_cart/': ('401'),
    '/api/users/subscriptions/': ('401'),
    '/api/ingredients/': (),
    '/api/ingredients/{}/': (),
}
API_POST_URLS = {
    'test_user_creation': '/api/users/',
    'test_user_set_password': '/api/users/set_password/',
    'test_user_login': '/api/auth/token/login/',
    'test_user_logout': '/api/auth/token/logout/',
    'test_recipe_creation': '/api/recipes/',
    'test_recipe_cart_add': '/api/recipes/2/shopping_cart/',
    'test_recipe_favorite_add': '/api/recipes/2/favorite/',
    'test_user_subscribe_add': '/api/users/2/subscribe/',
}
API_PATCH_URLS = {
    'test_recipe_patch': '/api/recipes/1/',
}
API_DELETE_URLS = {
    'test_recipe_delete': '/api/recipes/1/',
    'test_recipe_cart_delete': '/api/recipes/1/shopping_cart/',
    'test_recipe_favorite_delete': '/api/recipes/2/favorite/',
    'test_user_subscribe_delete': '/api/users/2/subscribe/',
}
FIRST_USER = {
    'username': 'first_user',
    'email': 'first_user@test.ru',
    'first_name': 'first_user',
    'last_name': 'first_user',
    'password': 'first_user',
}
SECOND_USER = {
    'username': 'second_user',
    'email': 'second_user@test.ru',
    'first_name': 'second_user',
    'last_name': 'second_user',
    'password': 'second_user',
}
TESTS_VALID_DATA = {
    'test_user_creation': {
        'email': 'vpupkin@yandex.ru',
        'username': 'vasya.pupkin',
        'first_name': 'Вася',
        'last_name': 'Пупкин',
        'password': get_random_string(12),
    },
    'test_user_set_password': {
        'new_password': get_random_string(12),
        'current_password': FIRST_USER['password'],
    },
    'test_user_login': {
        'email': FIRST_USER['email'],
        'password': FIRST_USER['password'],
    },
    'test_recipe_creation': {
        'ingredients': [
            {
                'id': 1,
                'amount': 10,
            }
        ],
        'tags': [
            1,
        ],
        'image': 'data:image/png;base64,oAAAAggCByxOyYQAAAABJRU5ErkJggg==',
        'name': 'string',
        'text': 'string',
        'cooking_time': 1,
    },
    'test_recipe_patch': {
        'ingredients': [
            {
                'id': 1,
                'amount': 5
            }
        ],
        'tags': [
            1,
        ],
        'image': 'data:image/png;base64,oAAAANSUhEUgAAAAEAAAABAgMAAABie==',
        'name': 'update_string',
        'text': 'update_string',
        'cooking_time': 5
    },
}
TESTS_INVALID_DATA = {
    'test_user_creation': {
        'email': 'invalid',
        'username': 'invalid@yandex.ru',
    },
    'test_user_set_password': {
        'new_password': get_random_string(12),
    },
    'test_user_login': {
        'email': '',
        'username': 'invalid',
    },
    'test_recipe_creation': {
        'name': 'string',
        'text': 'string',
        'cooking_time': 1,
    },
    'test_recipe_patch': {
        'cooking_time': 1,
    },
}
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED_IMG = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)


def create_user(username, email, first_name, last_name, password):
    """Создание тестового пользователя.
    """
    new_test_user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    new_test_user.set_password(password)
    new_test_user.save()

    return new_test_user


def create_tag(name='Test_tag', color='#FFFFFF', slug='test_slug'):
    """Создание тестового тэга.
    """
    return Tag.objects.create(
        name=name,
        color=color,
        slug=slug,
    )


def create_ingredient(name='Test_ingredient', measurement_unit='test_kg'):
    """Создание тестового ингредиента.
    """
    return Ingredients.objects.create(
        name=name,
        measurement_unit=measurement_unit,
    )


def create_recipe(author, tag, ingredient, name='Test_recipe'):
    """Создание тестового рецепта.
    """
    new_recipe = Recipe.objects.create(
        author=author,
        name=name,
        image=UPLOADED_IMG,
        text='test recipe text',
        cooking_time=1,
    )
    tag.save()
    new_recipe.save()
    new_recipe.tags.add(tag)
    IngredientsAmount(
        recipe=new_recipe,
        ingredients=ingredient,
        amount=1,
    )

    return new_recipe


def create_favorite(user, recipe):
    """Создание тестового избраного рецепта.
    """
    favorite = Favorite.objects.create(user=user)
    recipe.save()
    favorite.save()
    favorite.recipes.add(recipe)
    return favorite


def create_cart(user, recipe):
    """Создание тестовой карзины покупок.
    """
    cart = Cart.objects.create(user=user)
    recipe.save()
    cart.save()
    cart.recipes.add(recipe.pk)
    return cart


def create_subscribe(user, author):
    """Создание тестовой подписки на автора.
    """
    return Subscribe.objects.create(user=user, author=author)
