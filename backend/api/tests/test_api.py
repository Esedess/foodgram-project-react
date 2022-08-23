import inspect
import json
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, tag
from rest_framework import status
from rest_framework.test import APIClient

from . import fixtures as fixt
from recipes.models import Recipe

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()

client = APIClient()


def get_test_name():
    return inspect.getouterframes(inspect.currentframe())[1].function


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class GetAllUsersTest(TestCase):
    """ Test API """
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = fixt.create_user(**fixt.FIRST_USER)
        second_user = fixt.create_user(**fixt.SECOND_USER)
        tag = fixt.create_tag()
        ingredient = fixt.create_ingredient()
        recipe = fixt.create_recipe(self.user, tag, ingredient)
        fixt.create_recipe(self.user, tag, ingredient, name='ololo')
        fixt.create_favorite(self.user, recipe)
        fixt.create_cart(self.user, recipe)

        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)

        self.not_author_auth_client = APIClient()
        self.not_author_auth_client.force_authenticate(user=second_user)

    @tag('this')
    def test_urls_with_get(self):
        """Тестируем все API урлы GET запросом"""
        for url, expected_status in fixt.API_GET_URLS.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url.format(1))
                msg = f'{url} Не верный статус-код.'
                self.assertEqual(response.status_code, status.HTTP_200_OK, msg)
                if '401' in expected_status:
                    response = client.get(url.format(1))
                    self.assertEqual(
                        response.status_code,
                        status.HTTP_401_UNAUTHORIZED,
                        msg
                    )
                if '404' in expected_status:
                    response = self.auth_client.get(url.format(100))
                    self.assertEqual(
                        response.status_code, status.HTTP_404_NOT_FOUND, msg)

    @tag('api')
    def test_user_creation(self):
        """Тестируем создание пользователя"""
        user_count = User.objects.count()
        valid_data = fixt.TESTS_VALID_DATA.get(get_test_name())
        invalid_data = fixt.TESTS_INVALID_DATA.get(get_test_name())
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        msg = 'Создание пользователя с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(User.objects.count(), user_count, msg=msg)

        response = client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Создание пользователя с валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, msg=msg)
        self.assertEqual(User.objects.count(), user_count + 1, msg=msg)

        response = client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Создание пользователя с дублирующими валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(User.objects.count(), user_count + 1, msg=msg)

    @tag('api')
    def test_user_set_password(self):
        """Тестируем изменение пароля"""
        valid_data = fixt.TESTS_VALID_DATA.get(get_test_name())
        invalid_data = fixt.TESTS_INVALID_DATA.get(get_test_name())
        url = fixt.API_POST_URLS.get(get_test_name())

        response = self.auth_client.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        msg = 'Изменение пароля с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)

        response = client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Изменение пароля не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)

        response = self.auth_client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Изменение пароля пароль с валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)

    @tag('api')
    def test_user_login(self):
        """Тестируем возможность залогиниться"""
        valid_data = fixt.TESTS_VALID_DATA.get(get_test_name())
        invalid_data = fixt.TESTS_INVALID_DATA.get(get_test_name())
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        msg = 'Login с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)

        response = client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Login с валидными данными'
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=msg)

    @tag('api')
    def test_user_logout(self):
        """Тестируем возможность разлогиниться"""
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(url)
        msg = 'Loguot с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Loguot с валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)

    @tag('api')
    def test_recipe_creation(self):
        """Тестируем создание рецепта"""
        recipes_count = Recipe.objects.count()
        valid_data = fixt.TESTS_VALID_DATA.get(get_test_name())
        invalid_data = fixt.TESTS_INVALID_DATA.get(get_test_name())
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Создание рецепта с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count, msg=msg)

        response = self.auth_client.post(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        msg = 'Создание рецепта с невалидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count, msg=msg)

        response = self.auth_client.post(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Создание рецепта с валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count + 1, msg=msg)

    @tag('api')
    def test_recipe_patch(self):
        """Тестируем обновление рецепта"""
        valid_data = fixt.TESTS_VALID_DATA.get(get_test_name())
        invalid_data = fixt.TESTS_INVALID_DATA.get(get_test_name())
        url = fixt.API_PATCH_URLS.get(get_test_name())

        response = client.patch(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Обновление рецепта не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)

        response = self.auth_client.patch(
            url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        msg = 'Обновление рецепта не валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)

        response = self.not_author_auth_client.patch(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Обновление рецепта не автором'
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, msg=msg)

        response = self.auth_client.patch(
            url.replace('1', '999'),
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Удалось найти несуществующий рецепт?'
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, msg=msg)

        response = self.auth_client.patch(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        msg = 'Обновление рецепта валидными данными'
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=msg)

    @tag('api')
    def test_recipe_delete(self):
        """Тестируем удаление рецепта"""
        recipes_count = Recipe.objects.count()
        url = fixt.API_DELETE_URLS.get(get_test_name())

        response = client.delete(url)
        msg = 'Удаление рецепта не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count, msg=msg)

        response = self.not_author_auth_client.delete(url)
        msg = 'Удаление рецепта рецепт не автором'
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count, msg=msg)

        response = self.auth_client.delete(url.replace('1', '999'))
        msg = 'Удалось найти несуществующий рецепт?'
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count, msg=msg)

        response = self.auth_client.delete(url)
        msg = 'Удаление рецепта валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)
        self.assertEqual(Recipe.objects.count(), recipes_count - 1, msg=msg)

    @tag('api')
    def test_recipe_cart_add(self):
        """Тестируем добавление рецепта в корзину покупок"""
        recipes_in_cart = self.user.cart_set.get().recipes
        cart_recipes_count = recipes_in_cart.count()
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(url)
        msg = 'Добавление рецепта в корзину не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(recipes_in_cart.count(), cart_recipes_count, msg=msg)

        response = self.auth_client.post(url.replace('2', '999'))
        msg = 'Удалось найти несуществующий рецепт?'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(recipes_in_cart.count(), cart_recipes_count, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Добавление рецепта в корзину валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, msg=msg)
        self.assertEqual(
            recipes_in_cart.count(), cart_recipes_count + 1, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Добавление дублирующего рецепта в корзину'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            recipes_in_cart.count(), cart_recipes_count + 1, msg=msg)

    @tag('api')
    def test_recipe_cart_delete(self):
        """Тестируем удаление рецепта из корзины покупок"""
        recipes_in_cart = self.user.cart_set.get().recipes
        cart_recipes_count = recipes_in_cart.count()
        url = fixt.API_DELETE_URLS.get(get_test_name())

        response = client.delete(url)
        msg = 'Удаление рецепта из корзины не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(recipes_in_cart.count(), cart_recipes_count, msg=msg)

        response = self.auth_client.delete(url)
        msg = 'Удаление рецепта из корзины валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)
        self.assertEqual(
            recipes_in_cart.count(), cart_recipes_count - 1, msg=msg)

        response = self.auth_client.delete(url)
        msg = 'Повторное удаление рецепта из корзины валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            recipes_in_cart.count(), cart_recipes_count - 1, msg=msg)

    @tag('api')
    def test_recipe_favorite_add(self):
        """Тестируем добавление рецепта в избранное"""
        recipes_in_favorite = self.user.favorite_set.get().recipes
        favorite_recipes_count = recipes_in_favorite.count()
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(url)
        msg = 'Добавление рецепта в избранное не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count, msg=msg)

        response = self.auth_client.post(url.replace('2', '999'))
        msg = 'Удалось найти несуществующий рецепт?'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Добавление рецепта в избранное валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count + 1, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Повторное добавление рецепта в избранное'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count + 1, msg=msg)

    @tag('api')
    def test_recipe_favorite_delete(self):
        """Тестируем удаление рецепта из избранного"""
        recipes_in_favorite = self.user.favorite_set.get().recipes
        favorite_recipes_count = recipes_in_favorite.count()
        url = fixt.API_DELETE_URLS.get(get_test_name())

        response = client.delete(url)
        msg = 'Удаление рецепта из избранного не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count, msg=msg)

        response = self.auth_client.delete(url.replace('2', '1'))
        msg = 'Удаление рецепта из избранного валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count - 1, msg=msg)

        response = self.auth_client.delete(url)
        msg = 'Повторное удаление рецепта из избранного валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            recipes_in_favorite.count(), favorite_recipes_count - 1, msg=msg)

    @tag('api')
    def test_user_subscribe_add(self):
        """Тестируем подписку на автора"""
        authors_in_subscribe = self.user.subscriber.filter()
        subscribed_authors_count = authors_in_subscribe.count()
        url = fixt.API_POST_URLS.get(get_test_name())

        response = client.post(url)
        msg = 'Подписка на автора не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(), subscribed_authors_count, msg=msg)

        response = self.auth_client.post(url.replace('2', '999'))
        msg = 'Удалось найти несуществующего автора?'
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(), subscribed_authors_count, msg=msg)

        response = self.auth_client.post(url.replace('2', '1'))
        msg = 'Подписка на себя'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(), subscribed_authors_count, msg=msg)

        response = self.auth_client.post(url)
        msg = 'Подписка на автора валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(),
            subscribed_authors_count + 1,
            msg=msg,
        )

        response = self.auth_client.post(url)
        msg = 'Повторная подписка на автора'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(),
            subscribed_authors_count + 1,
            msg=msg,
        )

    @tag('api')
    def test_user_subscribe_delete(self):
        """Тестируем отмену подписки на автора"""
        subscribing_author = User.objects.get(id=2)
        fixt.create_subscribe(self.user, subscribing_author)
        authors_in_subscribe = self.user.subscriber.filter()
        subscribed_authors_count = authors_in_subscribe.count()
        url = fixt.API_DELETE_URLS.get(get_test_name())

        response = client.delete(url)
        msg = 'Отмена подписки на автора не авторизованным пользователем'
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(), subscribed_authors_count, msg=msg)

        response = self.auth_client.delete(url)
        msg = 'Отмена подписки на автора валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_204_NO_CONTENT, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(),
            subscribed_authors_count - 1,
            msg=msg,
        )

        response = self.auth_client.delete(url)
        msg = 'Повторная отмена подписки на автора валидными данными'
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST, msg=msg)
        self.assertEqual(
            authors_in_subscribe.count(),
            subscribed_authors_count - 1,
            msg=msg,
        )
