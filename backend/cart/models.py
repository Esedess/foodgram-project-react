from django.contrib.auth import get_user_model
from django.db import models

from food.models import Recipe

# from users import User
User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
        help_text='Должен быть заполнен.',
    )
    recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты',
        # through='IngredientsAmount',
        related_name='cart',
    )
