from django.test import TestCase
from django.urls import reverse
from farm.models import SeedLot, Event, Plant, Harvest, SeedlingBatch
from taxon.models import Taxon, Variety
from users.models import Organization
from django.utils import timezone
from media.models import Photo
from django.contrib.contenttypes.models import ContentType

class SeedLotDetailViewTests(TestCase):

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
            date_received=timezone.now(),
            organization=self.organization
        )
        self.photo = Photo.objects.create(
            image='path/to/photo.jpg',
            description='Test Photo',
            content_type=ContentType.objects.get_for_model(SeedLot),
            object_id=self.seedlot.id
        )

    def test_seedlot_detail_view(self):
        response = self.client.get(reverse('farm:seedlot_detail', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Seedlot')
        self.assertContains(response, 'Test Photo')
        self.assertTemplateUsed(response, 'farm/seedlot_detail.html')

class PlantDetailViewTests(TestCase):

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
            date=timezone.now(),
            location='Test Location',
            status='growing'
        )
        self.photo = Photo.objects.create(
            image='path/to/photo.jpg',
            description='Test Photo',
            content_type=ContentType.objects.get_for_model(Plant),
            object_id=self.plant.id
        )

    def test_plant_detail_view(self):
        response = self.client.get(reverse('farm:plant_detail', args=[self.plant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Variety - Test Location')
        self.assertContains(response, 'Test Photo')
        self.assertTemplateUsed(response, 'farm/plant_detail.html')

class HarvestDetailViewTests(TestCase):

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
            date=timezone.now(),
            status='growing'
        )
        self.harvest = Harvest.objects.create(
            date=timezone.now(),
            quantity=50,
            units='kg',
            description='Test Description',
            organization=self.organization
        )
        self.harvest.plants.add(self.plant)
        self.photo = Photo.objects.create(
            image='path/to/photo.jpg',
            description='Test Photo',
            content_type=ContentType.objects.get_for_model(Harvest),
            object_id=self.harvest.id
        )

    def test_harvest_detail_view(self):
        response = self.client.get(reverse('farm:harvest_detail', args=[self.harvest.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Harvest on')
        self.assertContains(response, 'Test Photo')
        self.assertTemplateUsed(response, 'farm/harvest_detail.html')

class SeedlingBatchDetailViewTests(TestCase):

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
            date=timezone.now(),
            quantity=200,
            units='seeds',
            status='germinating'
        )
        self.photo = Photo.objects.create(
            image='path/to/photo.jpg',
            description='Test Photo',
            content_type=ContentType.objects.get_for_model(SeedlingBatch),
            object_id=self.seedling_batch.id
        )

    def test_seedlingbatch_detail_view(self):
        response = self.client.get(reverse('farm:seedlingbatch_detail', args=[self.seedling_batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Seedlot batch sown on')
        self.assertContains(response, 'Test Photo')
        self.assertTemplateUsed(response, 'farm/seedlingbatch_detail.html')

class EventAddViewTests(TestCase):

    def setUp(self):
        self.event = Event.objects.create(
            type='planting',
            date=timezone.now(),
            description='Test Description'
        )

    def test_event_add_view(self):
        response = self.client.post(reverse('farm:event_add'), {
            'type': 'watering',
            'date': timezone.now().strftime('%Y-%m-%d'),  # Ensure date format is correct
            'description': 'Watering event'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after successful form submission
        self.assertTrue(Event.objects.filter(description='Watering event').exists())