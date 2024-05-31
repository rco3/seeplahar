# management/commands/assign_origin.py

from django.core.management.base import BaseCommand
from taxon.models import Variety

class Command(BaseCommand):
    help = 'Assign origin values from Variety to SeedLot and remove from Variety'

    def handle(self, *args, **kwargs):
        for variety in Variety.objects.all():
            seed_lots = variety.seed_lots.all()
            for seed_lot in seed_lots:
                seed_lot.origin = variety.origin
                seed_lot.save()
        self.stdout.write(self.style.SUCCESS('Successfully assigned origin values to SeedLots'))
