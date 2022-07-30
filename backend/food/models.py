from django.contrib.auth import get_user_model
from django.db import models

# from users import User
User = get_user_model()


class Tag(models.Model):
    # "name": "Завтрак",
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Имя тэга',
        help_text='Максимум 200 символов.'
    )
    # "color": "#E26C2D",
    color = models.CharField(
        unique=True,
        max_length=7,
        verbose_name='Цвет тэга',
        help_text='Цвет тэга.',
    )
    # "slug": "breakfast"
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Ссылка',
        help_text='Должна быть уникальным.',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    # "name": "Капуста",
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название ингридиента',
        help_text='Максимум 200 символов.',
    )
    # "measurement_unit": "кг"
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения',
        help_text='Максимум 200 символов.',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # "tags": [{}]
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='titles',
    )
    # "author": {}
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
        help_text='Должен быть заполнен.',
    )
    # "ingredients": [{}]
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингридиенты',
        through='IngredientsAmount',
        related_name='ingredients',
    )
    # "is_favorited": true,
    is_favorited = models.BooleanField(
        default=False,
    )
    # "is_in_shopping_cart": true,
    is_in_shopping_cart = models.BooleanField(
        default=False,
    )
    # "name": "string",
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название Рецепта',
        help_text='Максимум 200 символов.',
    )
    # "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    image = models.ImageField(
        upload_to='recipe/',
        verbose_name='Картинка рецепта',
        help_text='Введите текст рецепта.',
    )
    # "text": "string",
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите текст рецепта.',
    )
    # "cooking_time": 1
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Введите время приготовления в минутах.',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт',
    )
