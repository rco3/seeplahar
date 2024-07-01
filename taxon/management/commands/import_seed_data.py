import csv
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from taxon.models import Taxon, Variety, Characteristic
from farm.models import SeedLot

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import seed data from CSV files'

    def handle(self, *args, **kwargs):
        self.import_seed_varieties()
        self.import_tomato_seeds()

    def import_seed_varieties(self):
        with open('taxon/management/sample_data/seed_varieties.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                taxon_type = row['Type'].strip().lower()
                taxon, created = Taxon.objects.get_or_create(
                    name=row['Common Name'],
                    species_name=row['Species'],
                    defaults={'type': taxon_type}
                )
                logger.debug(f"Taxon: {taxon}, Created: {created}")

                variety, created = Variety.objects.get_or_create(
                    name=row['Variety'],
                    defaults={'taxon': taxon}
                )
                logger.debug(f"Variety: {variety}, Created: {created}")

                quantity, units = self.parse_amount(row['Amount'])
                SeedLot.objects.create(
                    variety=variety,
                    origin=row['Vendor'],
                    quantity=quantity,
                    units=units
                )
                logger.debug(f"SeedLot created for variety {variety}")

    def import_tomato_seeds(self):
        with open('taxon/management/sample_data/TomatoSeeds.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                logger.debug(f"Processing row: {row}")
                taxon, created = Taxon.objects.get_or_create(
                    name='Tomato',
                    species_name='solanum lycopersicum',
                    defaults={'type': 'vegetable'}
                )
                logger.debug(f"Taxon: {taxon}, Created: {created}")

                variety, created = Variety.objects.get_or_create(
                    name=row['Name'],
                    defaults={'taxon': taxon, 'description': row['Description']}
                )
                logger.debug(f"Variety: {variety}, Created: {created}")

                characteristics = {
                    'Planting Size': row['Planting Size'],
                    'Color': row['Color'],
                    'Shape': row['Shape'],
                    'Weight (Oz)': row['Oz  '],
                    'Days to Maturity': row['Days'],
                    'Family': row['Family'],
                    'Feature': row['Feature'],
                    'Breeder': row['Breeder'],
                }

                # Handle Antho separately to ensure multiple Colors
                colors = [row['Color']]
                if row['Antho']:
                    colors.append('Antho')

                # Add Color characteristics
                for color in colors:
                    if color:
                        char, created = Characteristic.objects.get_or_create(
                            name='Color',
                            value=color
                        )
                        logger.debug(f"Characteristic: {char}, Created: {created}")
                        variety.characteristics.add(char)
                        logger.debug(f"Added Characteristic {char} to Variety {variety}")

                # Add other characteristics
                for key, value in characteristics.items():
                    if key != 'Color' and value:  # Skip 'Color' as it's already handled
                        char, created = Characteristic.objects.get_or_create(
                            name=key,
                            value=value
                        )
                        logger.debug(f"Characteristic: {char}, Created: {created}")
                        variety.characteristics.add(char)
                        logger.debug(f"Added Characteristic {char} to Variety {variety}")

                if row['Source'] or row['Date Acq'] or row['QOH']:
                    SeedLot.objects.create(
                        variety=variety,
                        origin=row['Source'],
                        date_received=self.parse_date(row['Date Acq']),
                        quantity=self.parse_quantity(row['QOH']),
                        units='seeds'
                    )
                    logger.debug(f"SeedLot created for variety {variety}")

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%m/%d/%Y').date()
        except ValueError:
            logger.error(f"Date parsing error for date: {date_str}")
            return None

    def parse_quantity(self, quantity_str):
        try:
            return Decimal(quantity_str)
        except (ValueError, InvalidOperation):
            logger.error(f"Quantity parsing error for quantity: {quantity_str}")
            return Decimal('0')

    def parse_amount(self, amount_str):
        parts = amount_str.split()
        if len(parts) == 2:
            quantity, units = parts
            return self.parse_quantity(quantity), units
        logger.error(f"Amount parsing error for amount: {amount_str}")
        return Decimal('0'), 'units'
