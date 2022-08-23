from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
        error_messages={
            'unique': 'Пользователь с такой почтой уже существует.',
        },
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        help_text=(
            '150 символов или меньше.'
            'Только буквы, цифры и @/./+/-/_'),
        validators=(username_validator,),
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    first_name = models.CharField(
        'Имя',
        blank=False,
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        blank=False,
        max_length=150,
    )
    password = models.CharField(
        'Пароль',
        blank=False,
        max_length=150,
    )

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
        )

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='subscriber',
        verbose_name='Фоловер',
        help_text='Фоловер',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='subscribing',
        verbose_name='Автор',
        help_text='Автор',
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_following'),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='self_following',),
        )
