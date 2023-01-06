import csv
import os.path
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ('Import CSV-file into the base. '
            'Use command: python3 manage.py importcsv ingredients FILE.CSV'
            )
    BASES = {
        'ingredients': Ingredient,
        'tags': Tag,
    }

    def handle(self, *args, **options):
        if len(args) < 2:
            sys.exit(
                'Use command python3 manage.py importcsv table file.csv')
        if args[0].lower() not in self.BASES:
            sys.exit(
                f'Base unknown. Known bases are: {list(self.BASES.keys())}')
        if not os.path.exists(args[1]):
            sys.exit(
                f'File {args[1]} not exists!')
        base = self.BASES[args[0].lower()]
        if base == Tag:
            with open(args[1], 'r', encoding="utf-8") as csvfile:
                try:
                    reader = csv.reader(csvfile, delimiter=';')
                except Exception as e:
                    sys.exit(f'CSV-file read exception {e}')
                for row in reader:
                    try:
                        new_tag = base.objects.get_or_create(
                            name=row[0],
                            slug=row[1]
                        )
                        if new_tag[-1]:
                            print(
                                f'Создан новый тэг: {new_tag[0]}'
                            )
                        else:
                            print(
                                f'Тэг {new_tag[0]} создан ранее'
                            )
                    except Exception as e:
                        print(f'Exception {e}')
        if base == Ingredient:
            with open(args[1], 'r', encoding="utf-8") as csvfile:
                try:
                    reader = csv.reader(csvfile, delimiter=',')
                except Exception as e:
                    sys.exit(f'CSV-file read exception {e}')
                for row in reader:
                    try:
                        new_ingedient = base.objects.get_or_create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        if new_ingedient[-1]:
                            print(
                                f'Создан новый ингредиент: {new_ingedient[0]}'
                            )
                        else:
                            print(
                                f'Ингредиент {new_ingedient[0]} создан ранее'
                            )
                    except Exception as e:
                        print(f'Exception {e}')

    def add_arguments(self, parser):
        parser.add_argument(
            nargs='+',
            type=str,
            dest='args'
        )
