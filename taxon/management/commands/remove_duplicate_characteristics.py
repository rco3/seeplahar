# Create a new file `remove_duplicate_characteristics.py` in your `taxon/management/commands` folder

from django.core.management.base import BaseCommand
from taxon.models import Variety, Characteristic

class Command(BaseCommand):
    help = 'Remove duplicate characteristics from varieties'

    def handle(self, *args, **kwargs):
        varieties = Variety.objects.all()
        for variety in varieties:
            characteristics = variety.characteristics.all()
            unique_characteristics = set(characteristics)
            variety.characteristics.set(unique_characteristics)
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate characteristics'))
