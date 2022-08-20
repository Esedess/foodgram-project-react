from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Загружает ингредиенты. csv по умолчанию, json с флагом -j (--json)"

    def handle(self, *args, **options):
        if options.get('json'):
            from ._json import load_ingredient
            load_ingredient()
        else:
            from ._csv import load_ingredient
            load_ingredient()

    def add_arguments(self, parser):
        parser.add_argument(
            '-j',
            '--json',
            action='store_true',
            default=False,
            help='Загрузить ингридиенты из json'
        )
