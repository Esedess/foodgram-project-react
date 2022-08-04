from django.contrib.auth import get_user_model
from django.db import models

# from users import User
User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Имя тэга',
        help_text='Максимум 200 символов.'
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        verbose_name='Цвет тэга',
        help_text='Цвет тэга.',
    )
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
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название ингридиента',
        help_text='Максимум 200 символов.',
    )
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
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='tags',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
        help_text='Должен быть заполнен.',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        verbose_name='Ингридиенты',
        through='IngredientsAmount',
        related_name='ingredients',
    )
    is_favorited = models.BooleanField(
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
    )
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название Рецепта',
        help_text='Максимум 200 символов.',
    )
    image = models.ImageField(
        upload_to='recipe/',
        verbose_name='Картинка рецепта',
        help_text='Введите текст рецепта.',
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите текст рецепта.',
    )
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
    ingredients = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredients')


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
