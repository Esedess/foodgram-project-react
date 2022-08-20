from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    COLOR_PALETTE = (
        ('#FFFFFF', 'Белый'),
        ('#000000', 'Чёрный'),
        ('#0000FF', 'Синий'),
        ('#00FF00', 'Лайм'),
        ('#FF0000', 'Красный'),
        ('#FFFF00', 'Жёлтый'),
        ('#FFC0CB', 'Розовый'),
        ('#D2691E', 'Шоколадный'),
    )
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название тэга',
        help_text='Максимум 200 символов.'
    )
    color = ColorField(
        unique=True,
        samples=COLOR_PALETTE,
        max_length=7,
        verbose_name='Цвет тэга',
        help_text='В HEX формате - #000000',
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Ссылка',
        help_text='Должна быть уникальным.',
    )

    class Meta:
        ordering = ('-name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
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
        ordering = ('-name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )
        ]

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
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название Рецепта',
        help_text='Максимум 200 символов.',
    )
    image = models.ImageField(
        upload_to='recipe/',
        verbose_name='Картинка рецепта',
        help_text='Должен быть заполнен.',
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Введите текст рецепта.',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления в минутах',
        help_text='Минимально - 1 минута',
        validators=[
            MinValueValidator(1),
        ]
    )
    publication_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-publication_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredients = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE, verbose_name='Ингредиент',)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Минимально - 1 шт',
        validators=[
            MinValueValidator(1),
        ]
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'),
                name='unique_recipe_ingredient'
            )
        ]


class FavoriteAndCartBaseContent(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username


class Favorite(FavoriteAndCartBaseContent):

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Избраный рецепт'
        verbose_name_plural = 'Избраные рецепты'


class Cart(FavoriteAndCartBaseContent):

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
