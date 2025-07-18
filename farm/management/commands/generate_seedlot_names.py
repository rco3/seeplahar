# Create as: farm/management/commands/generate_seedlot_names.py

from django.core.management.base import BaseCommand
from django.db import transaction
from farm.models import SeedLot
from users.models import Customer
import re


class Command(BaseCommand):
    help = 'Generate proper names for SeedLots using VarNameAbbre+SourceAbbrev+Serial format'

    def abbreviate_name(self, name, max_length=10):
        """
        Create abbreviation from name: first 3 letters of each word, max 10 chars
        'Rebel Starfighter Prime' -> 'RebStaPri'
        'Wild Boar Farms' -> 'WilBoaFar'
        """
        if not name:
            return 'Unk'

        # Split on spaces and punctuation, remove empty strings
        words = [w for w in re.split(r'[^\w]+', name) if w]

        # Take first 3 letters of each word
        parts = []
        for word in words:
            if len(word) >= 3:
                parts.append(word[:3])
            else:
                parts.append(word)

        # Join and truncate to max_length
        abbrev = ''.join(parts)[:max_length]

        # Capitalize first letter of each original word part
        result = ''
        char_count = 0
        for word in words:
            if char_count >= len(abbrev):
                break
            word_len = min(3, len(word), len(abbrev) - char_count)
            if word_len > 0:
                result += abbrev[char_count].upper() + abbrev[char_count + 1:char_count + word_len].lower()
                char_count += word_len

        return result or 'Unk'

    def get_next_serial(self, variety_abbrev, source_abbrev, customer):
        """Find the next available serial number for this variety+source+customer combination"""
        base_name = f"{variety_abbrev}{source_abbrev}"

        # Find all existing seedlots with this base name pattern
        existing_names = SeedLot.objects.filter(
            customer=customer,
            name__startswith=base_name,
            name__regex=rf'^{re.escape(base_name)}\d{{2}}$'
        ).values_list('name', flat=True)

        # Extract serial numbers
        used_serials = set()
        for name in existing_names:
            if len(name) >= 2 and name[-2:].isdigit():
                used_serials.add(int(name[-2:]))

        # Find first available serial (01-99)
        for serial in range(1, 100):
            if serial not in used_serials:
                return f"{serial:02d}"

        # If all serials 01-99 are used, start with 00
        return "00"

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
                        # Get variety abbreviation
                        variety_name = seedlot.variety.name if seedlot.variety else 'Unknown'
                        variety_abbrev = self.abbreviate_name(variety_name, max_length=10)

                        # Get source abbreviation
                        if seedlot.source_partner:
                            source_name = seedlot.source_partner.name
                        elif seedlot.vendor:
                            source_name = seedlot.vendor
                        else:
                            source_name = 'Unknown'

                        source_abbrev = self.abbreviate_name(source_name, max_length=10)

                        # Ensure total length doesn't exceed 22 characters (base + 2 digit serial)
                        max_base_length = 20  # Leave room for 2-digit serial
                        base_length = len(variety_abbrev) + len(source_abbrev)

                        if base_length > max_base_length:
                            # Truncate proportionally
                            variety_max = min(len(variety_abbrev), max_base_length // 2)
                            source_max = max_base_length - variety_max
                            variety_abbrev = variety_abbrev[:variety_max]
                            source_abbrev = source_abbrev[:source_max]

                        # Get next serial number
                        serial = self.get_next_serial(variety_abbrev, source_abbrev, customer)

                        # Generate new name
                        new_name = f"{variety_abbrev}{source_abbrev}{serial}"

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