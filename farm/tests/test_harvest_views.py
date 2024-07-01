from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from farm.models import SeedLot, Planting, Harvest
from taxon.models import Taxon, Variety
from users.models import Customer
from django.utils import timezone

User = get_user_model()

class HarvestViewsTestCase(TestCase):
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
            customer=self.customer
        )
        self.harvest = Harvest.objects.create(
            date=timezone.now(),
            quantity=50,
            units="kg",
            description="First harvest of Andorian Blue Peas",
            customer=self.customer
        )
        self.harvest.plants.add(self.planting)

    def test_harvest_list_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:harvest_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First harvest of Andorian Blue Peas")

    def test_harvest_detail_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:harvest_detail', args=[self.harvest.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First harvest of Andorian Blue Peas")

    def test_harvest_create_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'plants': [self.planting.id],
            'date': timezone.now().date(),
            'quantity': 25,
            'units': 'kg',
            'description': 'Second harvest',
            'source_type': 'planting',
            'source_id': self.planting.id,
        }
        response = self.client.post(reverse('farm:harvest_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Harvest.objects.filter(description='Second harvest').exists())

    def test_harvest_update_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'plants': [self.planting.id],
            'date': timezone.now().date(),
            'quantity': 60,
            'units': 'kg',
            'description': 'Updated harvest description',
        }
        response = self.client.post(reverse('farm:harvest_update', args=[self.harvest.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.harvest.refresh_from_db()
        self.assertEqual(self.harvest.description, 'Updated harvest description')

    def test_harvest_delete_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.post(reverse('farm:harvest_delete', args=[self.harvest.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Harvest.objects.filter(id=self.harvest.id).exists())