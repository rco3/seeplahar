# Create as: farm/management/commands/migrate_seedlot_vendors.py

from django.core.management.base import BaseCommand
from django.db import transaction
from farm.models import SeedLot
from users.models import Partner, Customer


class Command(BaseCommand):
    help = 'Migrate SeedLot vendor text to Partner relationships'

    def handle(self, *args, **options):
        # Define the mapping
        vendor_mappings = {
            # Big 3: Source Partner only, vendor stays as text
            'American Seed': {'source_partner': 'American Seed', 'vendor': None},
            'Burpee': {'source_partner': 'Burpee', 'vendor': None},
            'Ferry-Morse': {'source_partner': 'Ferry-Morse', 'vendor': None},

            # Direct sellers: Both source partner and vendor
            'Bounty Hunter': {'source_partner': 'Bounty Hunter', 'vendor': 'Bounty Hunter'},
            'Wild Boar Farms': {'source_partner': 'Wild Boar Farms', 'vendor': 'Wild Boar Farms'},
            'TomatoFest': {'source_partner': 'TomatoFest', 'vendor': 'TomatoFest'},
            'Victory': {'source_partner': 'Victory', 'vendor': 'Victory'},
            'WoodlandCreationz (etsy)': {'source_partner': 'WoodlandCreationz', 'vendor': 'WoodlandCreationz (etsy)'},

            # Legacy cleanup (normalize case)
            'legacy': {'source_partner': 'Legacy', 'vendor': 'Legacy'},
            'Legacy': {'source_partner': 'Legacy', 'vendor': 'Legacy'},
            'Heritage': {'source_partner': 'Heritage', 'vendor': 'Heritage'},

            # Special case: Rockledge Gardens
            'Rockledge Gardens': {'source_partner': 'Botanical Interests', 'vendor': 'Rockledge Gardens'},
        }

        with transaction.atomic():
            total_updated = 0
            partners_created_summary = {}

            # Process all SeedLots across all customers
            for old_vendor, mapping in vendor_mappings.items():
                seedlots = SeedLot.objects.filter(vendor=old_vendor)

                for seedlot in seedlots:
                    # Get or create partner for THIS seedlot's customer
                    partner, created = Partner.objects.get_or_create(
                        name=mapping['source_partner'],
                        customer=seedlot.customer
                    )

                    # Track created partners
                    partner_key = f"{mapping['source_partner']} ({seedlot.customer.name})"
                    if created:
                        partners_created_summary[partner_key] = partner
                        self.stdout.write(f'Created Partner: {partner_key}')

                    # Update the seedlot
                    seedlot.source_partner = partner
                    seedlot.vendor = mapping['vendor']
                    seedlot.save()

                    total_updated += 1
                    self.stdout.write(
                        f'Updated SeedLot {seedlot.name} ({seedlot.customer.name}): '
                        f'vendor="{old_vendor}" -> "{mapping["vendor"]}", '
                        f'source_partner="{partner.name}"'
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {total_updated} SeedLots and created {len(partners_created_summary)} Partners'
                )
            )

        # Show summary by customer
        self.stdout.write('\n--- Summary by Customer ---')
        for customer in Customer.objects.all():
            customer_seedlots = SeedLot.objects.filter(customer=customer, source_partner__isnull=False)
            if customer_seedlots.exists():
                self.stdout.write(f'\n{customer.name}:')
                partners = customer_seedlots.values_list('source_partner__name', flat=True).distinct()
                for partner_name in sorted(partners):
                    count = customer_seedlots.filter(source_partner__name=partner_name).count()
                    self.stdout.write(f'  {partner_name}: {count} SeedLots')