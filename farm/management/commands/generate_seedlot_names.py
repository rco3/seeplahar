# farm/management/commands/generate_seedlot_names.py - Updated to use utilities

from django.core.management.base import BaseCommand
from django.db import transaction
from farm.models import SeedLot
from farm.utils.naming import generate_entity_name
from users.models import Customer


class Command(BaseCommand):
    help = 'Generate proper names for SeedLots using shared naming utilities'

    def handle(self, *args, **options):
        updated_count = 0
        error_count = 0

        # Group by customer for proper serial numbering
        for customer in Customer.objects.all():
            self.stdout.write(f'\nProcessing customer: {customer.name}')

            seedlots = SeedLot.objects.filter(customer=customer).select_related('variety', 'source_partner')

            with transaction.atomic():
                for seedlot in seedlots:
                    try:
                        variety_name = seedlot.variety.name if seedlot.variety else 'Unknown'

                        if seedlot.source_partner:
                            source_name = seedlot.source_partner.name
                        elif seedlot.vendor:
                            source_name = seedlot.vendor
                        else:
                            source_name = 'Unknown'

                        # Use the shared utility
                        new_name = generate_entity_name(variety_name, source_name, SeedLot, customer)

                        # Update the seedlot
                        old_name = seedlot.name
                        seedlot.name = new_name
                        seedlot.save()

                        self.stdout.write(f'  {old_name} -> {new_name}')
                        updated_count += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error processing SeedLot {seedlot.id}: {e}')
                        )
                        error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {updated_count} SeedLots renamed, {error_count} errors'
            )
        )

        # Show some examples
        self.stdout.write('\n--- Sample Results ---')
        for customer in Customer.objects.all():
            sample_seedlots = SeedLot.objects.filter(customer=customer)[:5]
            for seedlot in sample_seedlots:
                variety_name = seedlot.variety.name if seedlot.variety else 'Unknown'
                source_name = seedlot.source_partner.name if seedlot.source_partner else (seedlot.vendor or 'Unknown')
                self.stdout.write(f'{seedlot.name}: {variety_name} from {source_name}')