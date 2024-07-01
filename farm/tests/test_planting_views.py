from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from farm.models import SeedLot, Planting
from taxon.models import Taxon, Variety
from users.models import Customer
from django.utils import timezone

User = get_user_model()

class PlantingViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Starfleet Gardens")
        self.user = User.objects.create_user(username="picard", password="earlgrey", customer=self.customer)
        self.taxon = Taxon.objects.create(
            name="Andorian Blue Peas",
            species_name="Pisum andorii",
            type=Taxon.VEGETABLE,
            description="A vibrant blue pea from Andoria",
            customer=self.customer
        )
        self.variety = Variety.objects.create(
            name="Frost Resistant",
            taxon=self.taxon,
            description="Variety that can withstand extreme cold",
            customer=self.customer
        )
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name="Andorian Blue Pea Seeds Batch 1",
            quantity=100,
            units="grams",
            customer=self.customer
        )
        self.planting = Planting.objects.create(
            variety=self.variety,
            date=timezone.now(),
            location="Hydroponics Bay 1",
            status="growing",
            customer=self.customer,
            source_content_type=ContentType.objects.get_for_model(SeedLot),
            source_object_id=self.seedlot.id
        )

    def test_planting_list_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:planting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hydroponics Bay 1")

    def test_planting_detail_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:planting_detail', args=[self.planting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hydroponics Bay 1")

    def test_planting_create_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'variety': self.variety.id,
            'date': timezone.now().date(),
            'location': 'Hydroponics Bay 2',
            'status': 'growing',
            'source_type': 'seedlot',
            'source_id': self.seedlot.id,
        }
        response = self.client.post(reverse('farm:planting_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Planting.objects.filter(location='Hydroponics Bay 2').exists())

    def test_planting_update_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'variety': self.variety.id,
            'date': timezone.now().date(),
            'location': 'Updated Location',
            'status': 'harvested',
        }
        response = self.client.post(reverse('farm:planting_update', args=[self.planting.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.planting.refresh_from_db()
        self.assertEqual(self.planting.location, 'Updated Location')

    def test_planting_delete_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.post(reverse('farm:planting_delete', args=[self.planting.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Planting.objects.filter(id=self.planting.id).exists())