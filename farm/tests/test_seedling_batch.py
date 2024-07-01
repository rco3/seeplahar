from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from farm.models import SeedLot, SeedlingBatch
from taxon.models import Taxon, Variety
from users.models import Customer
from django.utils import timezone

User = get_user_model()

class SeedlingBatchViewsTestCase(TestCase):
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
        self.seedling_batch = SeedlingBatch.objects.create(
            seed_lot=self.seedlot,
            date=timezone.now(),
            quantity=50,
            units="seedlings",
            status="germinating",
            customer=self.customer
        )

    def test_seedlingbatch_list_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:seedlingbatch_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seedlings")

    def test_seedlingbatch_detail_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:seedlingbatch_detail', args=[self.seedling_batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seedlings")

    def test_seedlingbatch_create_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'seed_lot': self.seedlot.id,
            'date': timezone.now().date(),
            'quantity': 30,
            'units': 'seedlings',
            'status': 'germinating',
            'source_type': 'seedlot',
            'source_id': self.seedlot.id,
        }
        response = self.client.post(reverse('farm:seedlingbatch_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(SeedlingBatch.objects.filter(quantity=30).exists())

    def test_seedlingbatch_update_view(self):
        self.client.login(username="picard", password="earlgrey")
        data = {
            'seed_lot': self.seedlot.id,
            'date': timezone.now().date(),
            'quantity': 40,
            'units': 'seedlings',
            'status': 'transplanted',
        }
        response = self.client.post(reverse('farm:seedlingbatch_update', args=[self.seedling_batch.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.seedling_batch.refresh_from_db()
        self.assertEqual(self.seedling_batch.status, 'transplanted')

    def test_seedlingbatch_delete_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.post(reverse('farm:seedlingbatch_delete', args=[self.seedling_batch.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(SeedlingBatch.objects.filter(id=self.seedling_batch.id).exists())