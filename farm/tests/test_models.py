from django.test import TestCase
from farm.models import SeedLot, Planting, Harvest, SeedlingBatch, Event
from taxon.models import Taxon, Variety
from users.models import Customer, Partner
from django.contrib.contenttypes.models import ContentType
import uuid
from django.utils import timezone

class FarmModelTests(TestCase):

    def setUp(self):
        self.customer1 = Customer.objects.create(name='Galactic Gardeners')
        self.customer2 = Customer.objects.create(name='Martian Meadows')
        self.partner = Partner.objects.create(name='Andorian Seedlings', customer=self.customer1)

        self.taxon = Taxon.objects.create(
            name='Romulan Lettuce',
            species_name='Lactuca romulana',
            type=Taxon.VEGETABLE,
            description='A crisp, green lettuce with a slight metallic aftertaste',
            customer=self.customer1
        )
        self.variety = Variety.objects.create(
            name='Vulcan Crunch',
            taxon=self.taxon,
            description='Extra crispy variety, popular in Vulcan salads',
            customer=self.customer1
        )
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name='Starfleet Seed Stock',
            quantity=100,
            units='grams',
            date_received='2023-01-01',
            origin='USS Enterprise Hydroponics Bay',
            description='Prime seeds from the Enterprise',
            customer=self.customer1
        )
        self.planting = Planting.objects.create(
            variety=self.variety,
            date=timezone.now(),
            location="Hydroponics Bay 1",
            status="growing",
            customer=self.customer1
        )

    def test_seedlot_creation(self):
        self.assertEqual(self.seedlot.name, 'Starfleet Seed Stock')
        self.assertEqual(self.seedlot.quantity, 100)
        self.assertEqual(self.seedlot.units, 'grams')
        self.assertEqual(self.seedlot.customer, self.customer1)

    def test_seedlot_str_method(self):
        self.assertEqual(str(self.seedlot), 'Starfleet Seed Stock')

    def test_seedlot_customer_isolation(self):
        alien_seedlot = SeedLot.objects.create(
            variety=self.variety,
            name='Klingon Battle Seeds',
            quantity=50,
            units='grams',
            customer=self.customer2
        )
        self.assertEqual(SeedLot.objects.filter(customer=self.customer1).count(), 1)
        self.assertEqual(SeedLot.objects.filter(customer=self.customer2).count(), 1)

    def test_plant_creation_from_seedlot(self):
        plant = Planting.objects.create(
            variety=self.variety,
            date='2023-01-01',
            location='Holodeck Garden Simulation',
            status='growing',
            customer=self.customer1,
            source_content_type=ContentType.objects.get_for_model(SeedLot),
            source_object_id=self.seedlot.id
        )
        self.assertEqual(plant.location, 'Holodeck Garden Simulation')
        self.assertEqual(plant.status, 'growing')
        self.assertEqual(plant.customer, self.customer1)
        self.assertEqual(plant.source, self.seedlot)

    def test_plant_creation_from_partner(self):
        plant = Planting.objects.create(
            variety=self.variety,
            date='2023-01-01',
            location='Alien Botanical Gardens',
            status='growing',
            customer=self.customer1,
            source_partner=self.partner
        )
        self.assertEqual(plant.location, 'Alien Botanical Gardens')
        self.assertEqual(plant.status, 'growing')
        self.assertEqual(plant.customer, self.customer1)
        self.assertEqual(plant.source_partner, self.partner)
        self.assertIsNone(plant.source_object_id)

    def test_harvest_creation(self):
        plant = Planting.objects.create(
            variety=self.variety,
            date='2023-01-01',
            status='growing',
            customer=self.customer1,
            source_content_type=ContentType.objects.get_for_model(SeedLot),
            source_object_id=self.seedlot.id
        )
        harvest = Harvest.objects.create(
            date='2023-02-01',
            quantity=50,
            units='kg',
            description='First harvest of Romulan Lettuce',
            customer=self.customer1
        )
        harvest.plants.add(plant)
        self.assertEqual(harvest.quantity, 50)
        self.assertEqual(harvest.units, 'kg')
        self.assertEqual(harvest.customer, self.customer1)
        self.assertIn(plant, harvest.plants.all())

    def test_seedling_batch_creation(self):
        seedling_batch = SeedlingBatch.objects.create(
            seed_lot=self.seedlot,
            date='2023-01-01',
            quantity=200,
            units='seeds',
            status='germinating',
            customer=self.customer1
        )
        self.assertEqual(seedling_batch.quantity, 200)
        self.assertEqual(seedling_batch.units, 'seeds')
        self.assertEqual(seedling_batch.customer, self.customer1)

    def test_event_creation(self):
        event = Event.objects.create(
            type="fertilizing",
            date=timezone.now(),
            description="Fertilized Andorian Blue Peas",
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Planting),
            object_id=self.planting.id
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.type, "fertilizing")
        self.assertEqual(event.description, "Fertilized Andorian Blue Peas")
        self.assertEqual(event.customer, self.customer1)
        self.assertEqual(event.content_type, ContentType.objects.get_for_model(Planting))
        self.assertEqual(event.object_id, self.planting.id)

    def test_customer_isolation(self):
        # Create objects for both customers
        plant1 = Planting.objects.create(
            variety=self.variety,
            date='2023-01-01',
            status='growing',
            customer=self.customer1,
            source_content_type=ContentType.objects.get_for_model(SeedLot),
            source_object_id=self.seedlot.id
        )
        plant2 = Planting.objects.create(
            variety=self.variety,
            date='2023-01-01',
            status='growing',
            customer=self.customer2,
            source_partner=self.partner
        )

        # Check that each customer can only see their own objects
        self.assertEqual(Planting.objects.filter(customer=self.customer1).count(), 2)
        self.assertEqual(Planting.objects.filter(customer=self.customer2).count(), 1)

        # Check that total count is correct
        self.assertEqual(Planting.objects.count(), 3)