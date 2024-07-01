from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from farm.models import SeedLot
from taxon.models import Taxon, Variety
from users.models import Customer, Partner
from django.utils import timezone

User = get_user_model()

class SeedLotViewsTestCase(TestCase):
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

    def test_seedlot_list_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:seedlot_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Andorian Blue Pea Seeds Batch 1")

    def test_seedlot_detail_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:seedlot_detail', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Andorian Blue Pea Seeds Batch 1")

    def test_seedlot_create_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'variety': self.variety.id,
            'name': 'New SeedLot',
            'quantity': 200,
            'units': 'grams',
            'source_type': 'partner',
            'source_id': Partner.objects.create(name="Test Partner", customer=self.customer).id,
        }
        response = self.client.post(reverse('farm:seedlot_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(SeedLot.objects.filter(name='New SeedLot').exists())

    def test_seedlot_update_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'variety': self.variety.id,
            'name': 'Updated SeedLot',
            'quantity': 150,
            'units': 'grams',
        }
        response = self.client.post(reverse('farm:seedlot_update', args=[self.seedlot.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.seedlot.refresh_from_db()
        self.assertEqual(self.seedlot.name, 'Updated SeedLot')

    def test_seedlot_delete_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.post(reverse('farm:seedlot_delete', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(SeedLot.objects.filter(id=self.seedlot.id).exists())