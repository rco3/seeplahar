from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from farm.models import SeedLot, SeedlingBatch
from taxon.models import Taxon, Variety
from users.customer_context import CustomerContext
from users.models import Customer
from django.utils import timezone

User = get_user_model()


class SeedlingBatchViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Starfleet Gardens")

        with CustomerContext(self.customer):
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
                vendor="Starfleet Seed Cooperative",
                customer=self.customer
            )

            seedlot_ct = ContentType.objects.get_for_model(SeedLot)
            self.seedling_batch = SeedlingBatch.objects.create(
                variety=self.variety,
                date=timezone.now().date(),
                quantity=50,
                units="seedlings",
                location="Propagation Bay 1",
                vendor="Starfleet Seed Cooperative",
                source_content_type=seedlot_ct,
                source_object_id=self.seedlot.id,
                customer=self.customer
            )

        self.client.login(username="picard", password="earlgrey")

    def test_seedlingbatch_list_view(self):
        response = self.client.get(reverse('farm:seedlingbatch_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seedlings")

    def test_seedlingbatch_detail_view(self):
        response = self.client.get(reverse('farm:seedlingbatch_detail', args=[self.seedling_batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "seedlings")

    def test_seedlingbatch_create_view(self):
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        data = {
            'variety': self.variety.id,
            'date': timezone.now().date(),
            'quantity': 30,
            'units': 'seedlings',
            'location': 'Propagation Bay 2',
            'parent_batch': '',
            'vendor': 'Propagation Vendor',
            'source_partner': '',
            'source_content_type': seedlot_ct.id,
            'source_object_id': str(self.seedlot.id),
        }
        response = self.client.post(reverse('farm:seedlingbatch_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_batch = SeedlingBatch.objects.filter(quantity=30).first()
        self.assertIsNotNone(created_batch)
        self.assertEqual(created_batch.customer, self.customer)
        self.assertEqual(created_batch.source, self.seedlot)

    def test_seedlingbatch_update_view(self):
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        data = {
            'variety': self.variety.id,
            'date': timezone.now().date(),
            'quantity': 40,
            'units': 'seedlings',
            'location': 'Propagation Bay 3',
            'parent_batch': '',
            'vendor': 'Updated Vendor',
            'source_partner': '',
            'source_content_type': seedlot_ct.id,
            'source_object_id': str(self.seedlot.id),
        }
        response = self.client.post(reverse('farm:seedlingbatch_update', args=[self.seedling_batch.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.seedling_batch.refresh_from_db()
        self.assertEqual(self.seedling_batch.quantity, 40)
        self.assertEqual(self.seedling_batch.vendor, 'Updated Vendor')

    def test_seedlingbatch_delete_view(self):
        response = self.client.post(reverse('farm:seedlingbatch_delete', args=[self.seedling_batch.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(SeedlingBatch.objects.filter(id=self.seedling_batch.id).exists())
