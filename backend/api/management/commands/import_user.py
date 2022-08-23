from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string
from progress.spinner import LineSpinner

from users.models import User


class Command(BaseCommand):
    help = 'Загружает данные из csv или json'

    def handle(self, *args, **options):
        spinner = LineSpinner('Добавляем пользователей в базу ')
        spinner.next()
        super = User(
            username='admin',
            email='admin@admin.ru',
            first_name='admin',
            last_name='admin',
            is_staff=True,
            is_superuser=True,
        )
        password = 'admin'
        super.set_password(password)
        super.save()
        spinner.next()
        for row in DictReader(
            open(
                f'{settings.BASE_DIR}/data/users.csv',
                'r',
                encoding='utf8'
            )
        ):
            username, email, first_name, last_name = row.values()
            try:
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.set_password(get_random_string(10))
                user.save()
                spinner.next()
            except IntegrityError:
                print(
                    f'Юзер "{username}" уже есть в базе'
                )
        spinner.writeln('✓ Пользователи добавлены успешно!\n')
