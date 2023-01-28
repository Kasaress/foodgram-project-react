import csv
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = ('Import CSV-files. Use command: python3 manage.py importcsv')
    BASES = {
        'ingredients': Ingredient,
        'tags': Tag,
    }
    FILES = {
        'ingredients': f'{settings.DATA_ROOT}/ingredients.csv',
        'tags': f'{settings.DATA_ROOT}/tags.csv',
    }

    def _get_or_create_object(self, model, data):
        if model == Tag:
            return model.objects.get_or_create(
                                name=data['name'].lower(),
                                slug=data['slug']
                            )
        return model.objects.get_or_create(
                            name=data['name'].lower(),
                            measurement_unit=data['measurement_unit']
                        )

    def handle(self, *args, **options):
        for base_name, base in self.BASES.items():
            with open(self.FILES[base_name], 'r', encoding="utf-8") as csvfile:
                try:
                    reader = csv.DictReader(csvfile, delimiter=';')
                except Exception as e:
                    sys.exit(f'CSV-file read exception {e}')
                for row in reader:
                    try:
                        new_obj, status = self._get_or_create_object(base, row)
                        if status:
                            print(
                                f'Создан новый объект: "{new_obj}"'
                            )
                        else:
                            print(
                                f'Объект "{new_obj}" создан ранее'
                            )
                    except Exception as e:
                        print(f'Exception {e}')
