from csv import DictReader

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from progress.spinner import LineSpinner

from recipes.models import Tag


class Command(BaseCommand):
    help = "Загружает данные из csv или json"

    def handle(self, *args, **options):
        spinner = LineSpinner('Добавляем тэги в базу ')
        for row in DictReader(
            open(
                f'{settings.BASE_DIR}/data/tags.csv',
                'r',
                encoding="utf8"
            )
        ):
            spinner.next()
            name, color, slug = row.values()
            try:
                tag = Tag(
                    name=name,
                    color=color,
                    slug=slug,
                )
                tag.save()
            except IntegrityError:
                print(
                    f'Тэг "{name}" уже есть в базе'
                )
        spinner.writeln('✓ Тэги добавлены успешно!\n')
