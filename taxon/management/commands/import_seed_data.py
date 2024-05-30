import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from taxon.models import Taxon, Variety, Characteristic
from farm.models import SeedLot

class Command(BaseCommand):
    help = 'Import seed data into the Variety and SeedLot models'

    def handle(self, *args, **kwargs):
        # Paths to your CSV files
        csv_file_path1 = './taxon/management/sample_data/seed_varieties.csv'
        csv_file_path2 = './taxon/management/sample_data/TomatoSeeds.csv'

        # Define a function to parse date
        def parse_date(date_str):
            try:
                return datetime.strptime(date_str, '%m/%d/%Y').date() if date_str else None
            except ValueError:
                return None

        # Function to get value or None
        def get_value_or_none(row, key):
            return row.get(key, None) if row.get(key, "").strip() else None

        # Import data from the first CSV file
        with open(csv_file_path1, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                type_value = row['Type'].lower()  # Normalize type to lowercase
                taxon, _ = Taxon.objects.get_or_create(
                    name=row['Common Name'],
                    defaults={'species_name': row['Species'], 'type': type_value}
                )
                variety, created = Variety.objects.get_or_create(
                    name=row['Variety'],
                    taxon=taxon,
                    defaults={'description': '', 'origin': row['Vendor']}
                )
                quantity = int(row['Amount'].split()[0]) if row['Amount'].split()[0].isdigit() else None
                SeedLot.objects.create(
                    variety=variety,
                    quantity=quantity,
                    date_received=parse_date(get_value_or_none(row, 'Date Acq'))
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created variety: {variety.name}'))

        # Import data from the second CSV file
        with open(csv_file_path2, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                taxon, _ = Taxon.objects.get_or_create(
                    name='Tomato',
                    defaults={'species_name': row['Species'], 'type': 'vegetable'}
                )
                variety, created = Variety.objects.get_or_create(
                    name=row['Name'],
                    taxon=taxon,
                    defaults={'description': row['Description'], 'origin': row['Source']}
                )
                quantity = int(row['QOH']) if row['QOH'] and row['QOH'].isdigit() else None
                SeedLot.objects.create(
                    variety=variety,
                    quantity=quantity,
                    date_received=parse_date(get_value_or_none(row, 'Date Acq'))
                )
                characteristics = [
                    ('Plant Size', get_value_or_none(row, 'Plant Size')),
                    ('Color', get_value_or_none(row, 'Color')),
                    ('Shape', get_value_or_none(row, 'Shape')),
                    ('Weight, Oz', get_value_or_none(row, 'Oz')),
                    ('Days', get_value_or_none(row, 'Days')),
                    ('Family', get_value_or_none(row, 'Family')),
                    ('Feature', get_value_or_none(row, 'Feature')),
                    ('Antho', 'Yes' if row.get('Antho') else 'No'),
                    ('Notes', get_value_or_none(row, 'Notes')),
                    ('Breeder', get_value_or_none(row, 'Breeder')),
                ]
                for name, value in characteristics:
                    if value:
                        Characteristic.objects.create(
                            variety=variety,
                            name=name,
                            value=value
                        )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created variety: {variety.name}'))
