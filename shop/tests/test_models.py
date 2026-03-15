from django.test import TestCase
from shop.models import SeedPackage, ProducePackage, PlantPackage
from farm.models import SeedLot, Harvest, Planting, Location
from taxon.models import Taxon, Variety
from users.models import Customer
from users.customer_context import CustomerContext
from django.utils import timezone

class ShopModelsTestCase(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer")
        self.taxon = Taxon.objects.create(
            name="Test Taxon",
            species_name="Test Species",
            type=Taxon.VEGETABLE,
            customer=self.customer
        )
        self.variety = Variety.objects.create(
            name="Test Variety",
            taxon=self.taxon,
            customer=self.customer
        )
        self.seed_lot = SeedLot.objects.create(
            name="Test Seed Lot",
            variety=self.variety,
            quantity=100,
            units="seeds",
            customer=self.customer
        )
        with CustomerContext(self.customer):
            self.location = Location.objects.create(name="Test Location", customer=self.customer)
            self.planting = Planting.objects.create(
                variety=self.variety,
                date=timezone.now(),
                location=self.location,
                status="growing",
                customer=self.customer
            )
        self.harvest = Harvest.objects.create(
            variety=self.variety,
            date=timezone.now(),
            quantity=50,
            units="kg",
            customer=self.customer
        )
        self.harvest.plants.add(self.planting)

    def test_seed_package_creation(self):
        seed_package = SeedPackage.objects.create(
            seed_lot=self.seed_lot,
            quantity=10,
            quantity_units="seeds",
            date_packaged=timezone.now(),
            customer=self.customer
        )
        self.assertIsNotNone(seed_package.id)
        self.assertEqual(str(seed_package), f'Seed Package: {self.seed_lot.name} - 10 seeds')

    def test_produce_package_creation(self):
        produce_package = ProducePackage.objects.create(
            harvest=self.harvest,
            quantity=5,
            quantity_units="kg",
            date_packaged=timezone.now(),
            customer=self.customer
        )
        self.assertIsNotNone(produce_package.id)
        self.assertEqual(str(produce_package), f'Produce Package: {self.harvest} - 5 kg')

    def test_plant_package_creation(self):
        plant_package = PlantPackage.objects.create(
            date_packaged=timezone.now(),
            quantity=3,
            customer=self.customer
        )
        plant_package.plants.add(self.planting)
        self.assertIsNotNone(plant_package.id)
        self.assertEqual(str(plant_package), f'Planting Package created on {plant_package.date_packaged}')
        self.assertEqual(plant_package.plants.count(), 1)