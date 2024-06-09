from django.test import TestCase
from farm.models import SeedLot, Plant, Harvest, SeedlingBatch, Event
from taxon.models import Taxon, Variety
from users.models import Organization
import uuid
from django.utils import timezone

class SeedLotModelTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )
        self.variety = Variety.objects.create(
            name='Test Variety',
            taxon=self.taxon,
            description='Test Variety Description'
        )
        self.organization = Organization.objects.create(name='Test Organization')
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name='Test Seedlot',
            quantity=100,
            units='grams',
            date_received='2023-01-01',
            origin='Test Origin',
            description='Test Description',
            organization=self.organization
        )

    def test_seedlot_creation(self):
        self.assertEqual(self.seedlot.name, 'Test Seedlot')
        self.assertEqual(self.seedlot.quantity, 100)
        self.assertEqual(self.seedlot.units, 'grams')

    def test_seedlot_str_method(self):
        self.assertEqual(str(self.seedlot), 'Test Seedlot')

    def test_seedlot_update(self):
        self.seedlot.name = 'Updated Seedlot'
        self.seedlot.save()
        self.assertEqual(self.seedlot.name, 'Updated Seedlot')

    def test_seedlot_deletion(self):
        seedlot_id = self.seedlot.id
        self.seedlot.delete()
        self.assertFalse(SeedLot.objects.filter(id=seedlot_id).exists())

class PlantModelTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )
        self.variety = Variety.objects.create(
            name='Test Variety',
            taxon=self.taxon,
            description='Test Variety Description'
        )
        self.organization = Organization.objects.create(name='Test Organization')
        self.seedlot = SeedLot.objects.create(variety=self.variety, name='Test Seedlot', quantity=100)
        self.plant = Plant.objects.create(
            seed_lot=self.seedlot,
            variety=self.variety,
            date='2023-01-01',
            location='Test Location',
            status='growing'
        )

    def test_plant_creation(self):
        self.assertEqual(self.plant.location, 'Test Location')
        self.assertEqual(self.plant.status, 'growing')

    def test_plant_str_method(self):
        self.assertEqual(str(self.plant), 'Test Variety - Test Location')

    def test_plant_update(self):
        self.plant.status = 'harvested'
        self.plant.save()
        self.assertEqual(self.plant.status, 'harvested')

    def test_plant_deletion(self):
        plant_id = self.plant.id
        self.plant.delete()
        self.assertFalse(Plant.objects.filter(id=plant_id).exists())

class HarvestModelTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )
        self.variety = Variety.objects.create(
            name='Test Variety',
            taxon=self.taxon,
            description='Test Variety Description'
        )
        self.organization = Organization.objects.create(name='Test Organization')
        self.plant = Plant.objects.create(
            variety=self.variety,
            date='2023-01-01',
            status='growing'
        )
        self.harvest = Harvest.objects.create(
            date='2023-02-01',
            quantity=50,
            units='kg',
            description='Test Description',
            organization=self.organization
        )
        self.harvest.plants.add(self.plant)

    def test_harvest_creation(self):
        self.assertEqual(self.harvest.quantity, 50)
        self.assertEqual(self.harvest.units, 'kg')

    def test_harvest_str_method(self):
        self.assertEqual(str(self.harvest), 'Harvest on 2023-02-01')

    def test_harvest_update(self):
        self.harvest.quantity = 60
        self.harvest.save()
        self.assertEqual(self.harvest.quantity, 60)

    def test_harvest_deletion(self):
        harvest_id = self.harvest.id
        self.harvest.delete()
        self.assertFalse(Harvest.objects.filter(id=harvest_id).exists())

class SeedlingBatchModelTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )
        self.variety = Variety.objects.create(
            name='Test Variety',
            taxon=self.taxon,
            description='Test Variety Description'
        )
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name='Test Seedlot',
            quantity=100
        )
        self.seedling_batch = SeedlingBatch.objects.create(
            seed_lot=self.seedlot,
            date='2023-01-01',
            quantity=200,
            units='seeds',
            status='germinating'
        )

    def test_seedlingbatch_creation(self):
        self.assertEqual(self.seedling_batch.quantity, 200)
        self.assertEqual(self.seedling_batch.units, 'seeds')

    def test_seedlingbatch_str_method(self):
        self.assertEqual(str(self.seedling_batch), 'Test Seedlot batch sown on 2023-01-01')

    def test_seedlingbatch_update(self):
        self.seedling_batch.status = 'transplanted'
        self.seedling_batch.save()
        self.assertEqual(self.seedling_batch.status, 'transplanted')

    def test_seedlingbatch_deletion(self):
        seedlingbatch_id = self.seedling_batch.id
        self.seedling_batch.delete()
        self.assertFalse(SeedlingBatch.objects.filter(id=seedlingbatch_id).exists())

class EventModelTests(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            type='planting',
            date='2023-01-01',
            description='Test Description'
        )

    def test_event_creation(self):
        self.assertEqual(self.event.type, 'planting')
        self.assertEqual(self.event.description, 'Test Description')

    def test_event_str_method(self):
        self.assertEqual(str(self.event), 'Event: planting on 2023-01-01')

    def test_event_update(self):
        self.event.type = 'watering'
        self.event.save()
        self.assertEqual(self.event.type, 'watering')

    def test_event_deletion(self):
        event_id = self.event.id
        self.event.delete()
        self.assertFalse(Event.objects.filter(id=event_id).exists())
