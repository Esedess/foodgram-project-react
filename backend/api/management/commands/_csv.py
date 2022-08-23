from csv import DictReader

from django.conf import settings
from django.db.utils import IntegrityError
from progress.spinner import LineSpinner

from recipes.models import Ingredients


def load_ingredient():
    spinner = LineSpinner('Добавляем ингридиенты в базу ')
    for row in DictReader(
        open(
            f'{settings.BASE_DIR}/data/ingredients.csv',
            'r',
            encoding='utf8'
        )
    ):
        spinner.next()
        name, measurement_unit = row.values()
        try:
            ingredient = Ingredients(
                name=name,
                measurement_unit=measurement_unit,
            )
            ingredient.save()
        except IntegrityError:
            print(
                f'"{name},{measurement_unit}" уже есть в базе'
            )
    spinner.writeln('✓ Ингредиенты добавлены успешно!\n')
