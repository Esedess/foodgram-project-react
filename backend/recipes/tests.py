import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings, tag

from .models import Cart, Favorite, Ingredients, IngredientsAmount, Recipe, Tag

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


# Поля моделие
STR = {
    'Tag': 'name',
    'Ingredients': 'name',
    'Recipe': 'name',
    'Favorite': 'user.username',
    'Cart': 'user.username',
}
FIELDS_VERBOSES = {
    'Tag': {
        'name': 'Название тэга',
        'color': 'Цвет тэга',
        'slug': 'Ссылка',
    },
    'Ingredients': {
        'name': 'Название ингридиента',
        'measurement_unit': 'Единица измерения',
    },
    'Recipe': {
        'tags': 'Тэги',
        'author': 'Автор',
        'ingredients': 'Ингридиенты',
        'name': 'Название Рецепта',
        'image': 'Картинка рецепта',
        'text': 'Текст рецепта',
        'cooking_time': 'Время приготовления в минутах',
        'publication_date': 'Дата публикации',
    },
    'Favorite': {
        'user': 'Пользователь',
        'recipes': 'Рецепты',
    },
    'Cart': {
        'user': 'Пользователь',
        'recipes': 'Рецепты',
    },
}
META_VERBOSE_NAME = {
    'Tag': 'Тэг',
    'Ingredients': 'Ингредиент',
    'Recipe': 'Рецепт',
    'Favorite': 'Избраный рецепт',
    'Cart': 'Корзина покупок',
}
META_VERBOSE_NAME_PLURAL = {
    'Tag': 'Тэги',
    'Ingredients': 'Ингредиенты',
    'Recipe': 'Рецепты',
    'Favorite': 'Избраные рецепты',
    'Cart': 'Корзины покупок',
}
META_ORDERING = {
    'Tag': ('-name',),
    'Ingredients': ('-name',),
    'Recipe': ('-publication_date',),
    'Favorite': ('-user',),
    'Cart': ('-user',),
}


def create_user(
    username='Test_user',
    email='test@test.ru',
    first_name='test',
    last_name='test',
    password='test',
):
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
    return Tag(
        name=name,
        color=color,
        slug=slug,
    )


def create_ingredient(name='Test_ingredient', measurement_unit='test_kg'):
    """Создание тестового ингредиента.
    """
    return Ingredients(
        name=name,
        measurement_unit=measurement_unit,
    )


def create_recipe(author, name, tag, ingredient):
    """Создание тестового рецепта.
    """
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
    new_recipe = Recipe(
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


def get_class_name(obj):
    return obj.__class__.__name__


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class RecipesModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = create_user()
        cls.tag = create_tag()
        cls.ingredient = create_ingredient()
        cls.recipe = create_recipe(
            cls.user,
            'test_recipe',
            cls.tag,
            cls.ingredient,
        )
        cls.favorite = create_favorite(cls.user, cls.recipe)
        cls.cart = create_cart(cls.user, cls.recipe)
        cls.instanses = (
            cls.tag,
            cls.ingredient,
            cls.recipe,
            cls.favorite,
            cls.cart,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @tag('models')
    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for instans in self.instanses:
            class_name = get_class_name(instans)
            str_attr = STR[class_name]
            if '.' in str_attr:
                first, second = str_attr.split('.')
                expected_str = getattr(getattr(instans, first), second)
            else:
                expected_str = getattr(instans, str_attr)
            msg = f'Модель {class_name} - не верный __str__'
            self.assertEqual(expected_str, str(instans), msg=msg)

    @tag('models')
    def test_models_have_correct_verbose_name(self):
        """Проверяем, что у моделей корректные verbose_name."""
        for instans in self.instanses:
            class_name = get_class_name(instans)

            for field, expected_value in FIELDS_VERBOSES[class_name].items():
                msg = f'{class_name}.{field} - не верный verbose_name'
                with self.subTest(field=field):
                    self.assertEqual(
                        instans._meta.get_field(field).verbose_name,
                        expected_value,
                        msg=msg,
                    )
            msg = f'{class_name} - не верный Meta verbose_name'
            self.assertEqual(
                instans._meta.verbose_name,
                META_VERBOSE_NAME[class_name],
                msg=msg,
            )
            msg = f'{class_name} - не верный Meta verbose_name_plural'
            self.assertEqual(
                instans._meta.verbose_name_plural,
                META_VERBOSE_NAME_PLURAL[class_name],
                msg=msg,
            )

    @tag('models')
    def test_models_have_correct_ordering(self):
        """Проверяем, что тэги правильно сортируются."""
        for instans in self.instanses:
            class_name = get_class_name(instans)
            msg = f'{class_name} - не верный Meta verbose_name_plural'
            self.assertEqual(
                instans._meta.ordering,
                META_ORDERING[class_name],
                msg=msg,
            )
