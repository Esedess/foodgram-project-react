from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Загружает данные из csv или json'

    def handle(self, *args, **options):
        from .import_ingredient import Command
        Command.handle(self)

        from .import_user import Command
        Command.handle(self)

        from .import_tag import Command
        Command.handle(self)
