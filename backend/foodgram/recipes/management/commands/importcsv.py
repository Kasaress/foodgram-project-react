import csv
import os.path
import sys

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = ('Import CSV-file into the base. '
            'Use command: python3 manage.py importcsv table FILE.CSV'
            )
    BASES = {
        'table': Ingredient,
    }

    def handle(self, *args, **options):
        if len(args) < 2:
            sys.exit(
                'Too low arguments!python3 manage.py importcsv table file.csv')
        if args[0].lower() not in self.BASES:
            sys.exit(
                f'Base unknown. Known bases are: {list(self.BASES.keys())}')
        if not os.path.exists(args[1]):
            sys.exit(
                f'File {args[1]} not exists!')
        base = Ingredient
        with open(args[1], 'r', encoding="utf-8") as csvfile:
            try:
                reader = csv.reader(csvfile, delimiter=",")
            except Exception as e:
                sys.exit(f'CSV-file read exception {e}')
            writed_rows = 0
            for row in reader:
                try:
                    base.objects.create(
                        name=row[0],
                        measurement_unit=row[1])
                    writed_rows += 1
                except Exception as e:
                    print(f'Exception {e}')
                finally:
                    print(
                        f'Added {writed_rows} rows to base {args[0].lower()}'
                    )

    def add_arguments(self, parser):
        parser.add_argument(
            nargs='+',
            type=str,
            dest='args'
        )
