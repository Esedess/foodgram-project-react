from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings, tag

from .models import Follow

User = get_user_model()


# Поля модели User
USER_FIELDS_VERBOSES = {
    'email': 'Адрес электронной почты',
    'username': 'Имя пользователя',
    'first_name': 'Имя',
    'last_name': 'Фамилия',
    'password': 'Пароль',
}
USER_META_VERBOSE_NAME = 'Пользователь'
USER_META_VERBOSE_NAME_PLURAL = 'Пользователи'
USER_META_ORDERING = ('-date_joined',)

# Поля модели Follow
FOLLOW_FIELDS_VERBOSES = {
    'user': 'Фоловер',
    'author': 'Автор',
}
FOLLOW_META_VERBOSE_NAME = 'Подписка'
FOLLOW_META_VERBOSE_NAME_PLURAL = 'Подписки'
FOLLOW_META_ORDERING = ('-user',)


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


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_database',
    }
})
class UserModelTest(TestCase):
    def setUp(self):
        self.user = create_user()

    @tag('models')
    def test_user_model_have_correct_object_names(self):
        """Проверяем, что у модели User корректно работает __str__."""
        expected_user_str = self.user.username
        self.assertEqual(expected_user_str, str(self.user))

    @tag('models')
    def test_user_verbose_name(self):
        """Проверяем, что у модели User корректные verbose_name."""
        for field, expected_value in USER_FIELDS_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.user._meta.get_field(field).verbose_name,
                    expected_value
                )
        self.assertEqual(
            self.user._meta.verbose_name,
            USER_META_VERBOSE_NAME,
        )
        self.assertEqual(
            self.user._meta.verbose_name_plural,
            USER_META_VERBOSE_NAME_PLURAL,
        )

    @tag('models')
    def test_user_ordering(self):
        """Проверяем, что пользователи правильно сортируются."""
        self.assertEqual(self.user._meta.ordering, USER_META_ORDERING)


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_database',
    }
})
class FollowModelTest(TestCase):
    def setUp(self):
        self.follower = create_user()
        self.following = create_user(
            username='Test_following',
            email='following@test.ru',
        )
        self.follow = Follow.objects.create(
            user=self.follower,
        )
        self.follow.author.add(self.following)

    @tag('models')
    def test_follow_verbose_name(self):
        """Проверяем, что у модели Follow корректные verbose_name."""
        follow = self.follow
        for field, expected_value in FOLLOW_FIELDS_VERBOSES.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value
                )
        self.assertEqual(
            follow._meta.verbose_name,
            FOLLOW_META_VERBOSE_NAME,
        )
        self.assertEqual(
            follow._meta.verbose_name_plural,
            FOLLOW_META_VERBOSE_NAME_PLURAL,
        )

    @tag('models')
    def test_follow_ordering(self):
        """Проверяем, что подписки правильно сортируются."""
        follow = self.follow
        self.assertEqual(follow._meta.ordering, FOLLOW_META_ORDERING)
