from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from taxon.models import Variety, Taxon
from farm.models import SeedLot
from users.customer_context import CustomerContext
from users.models import Customer
import uuid

User = get_user_model()


class GenericDetailViewTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name='Test Customer')

        # Create a Taxon
        with CustomerContext(self.customer):
            self.taxon = Taxon.objects.create(
                id=uuid.uuid4(),
                name='Test Taxon',
                description='Test description for taxon',
                species_name='Test species',
                type=Taxon.VEGETABLE,
                customer=self.customer
            )

            # Create a Variety
            self.variety = Variety.objects.create(
                id=uuid.uuid4(),
                name='Test Variety',
                taxon=self.taxon,
                description='Test description for variety',
                customer=self.customer
            )

            # Create SeedLot
            self.seedlot = SeedLot.objects.create(
                id=uuid.uuid4(),
                variety=self.variety,
                quantity=100,
                vendor='Test SeedLot Vendor',
                date_received=timezone.now().date(),
                customer=self.customer
            )

        with CustomerContext(self.customer):
            self.user = User.objects.create_user(
                username='viewer', password='testpass', customer=self.customer
            )

        self.client.login(username='viewer', password='testpass')

    def test_variety_detail_view(self):
        with CustomerContext(self.customer):
            response = self.client.get(
                reverse('generic_detail', args=['taxon', 'variety', str(self.variety.id)])
            )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taxon/variety_detail.html')
        self.assertContains(response, self.variety.name)
        self.assertContains(response, self.variety.description)

    def test_taxon_detail_view(self):
        with CustomerContext(self.customer):
            response = self.client.get(
                reverse('generic_detail', args=['taxon', 'taxon', str(self.taxon.id)])
            )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taxon/taxon_detail.html')
        self.assertContains(response, self.taxon.name)
        self.assertContains(response, self.taxon.description)

    def test_404_for_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        with CustomerContext(self.customer):
            response = self.client.get(
                reverse('generic_detail', args=['taxon', 'taxon', str(invalid_uuid)])
            )
        self.assertEqual(response.status_code, 404)
