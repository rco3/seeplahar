from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from taxon.models import Variety, Taxon
from farm.models import SeedLot
from farm.tests.base import FarmBaseTestCase
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


class UniversalDetailViewTests(FarmBaseTestCase):
    """
    Tests for the /<uuid>/ universal QR scan entry point.
    Each entity type should redirect to its named detail URL.
    Cross-tenant UUIDs and unknown UUIDs should 404.
    """

    def setUp(self):
        super().setUp()
        self.login_test_user()

    def _universal_url(self, pk):
        return reverse('universal-detail', kwargs={'pk': pk})

    # --- per-entity redirect tests ---

    def test_seedlot_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.seedlot.id))
        self.assertRedirects(
            response,
            reverse('farm:seedlot_detail', kwargs={'pk': self.seedlot.id}),
            fetch_redirect_response=False,
        )

    def test_planting_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.planting.id))
        self.assertRedirects(
            response,
            reverse('farm:planting_detail', kwargs={'pk': self.planting.id}),
            fetch_redirect_response=False,
        )

    def test_harvest_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.harvest.id))
        self.assertRedirects(
            response,
            reverse('farm:harvest_detail', kwargs={'pk': self.harvest.id}),
            fetch_redirect_response=False,
        )

    def test_seedlingbatch_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.seedling_batch.id))
        self.assertRedirects(
            response,
            reverse('farm:seedlingbatch_detail', kwargs={'pk': self.seedling_batch.id}),
            fetch_redirect_response=False,
        )

    def test_variety_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.variety.id))
        self.assertRedirects(
            response,
            reverse('taxon:variety_detail', kwargs={'pk': self.variety.id}),
            fetch_redirect_response=False,
        )

    def test_taxon_redirects_to_detail(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(self.taxon.id))
        self.assertRedirects(
            response,
            reverse('taxon:taxon_detail', kwargs={'pk': self.taxon.id}),
            fetch_redirect_response=False,
        )

    # --- failure cases ---

    def test_unknown_uuid_returns_404(self):
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(uuid.uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_other_tenant_uuid_returns_404(self):
        """Worf's seedlot UUID should be invisible to Picard."""
        with CustomerContext(self.other_customer):
            other_seedlot = SeedLot.objects.create(
                variety=self.variety,
                name='Klingon Battle Seeds',
                quantity=50,
                vendor='House Martok',
                date_received=timezone.now().date(),
                customer=self.other_customer,
            )
        # Picard is logged in (setUp calls login_test_user)
        with CustomerContext(self.customer):
            response = self.client.get(self._universal_url(other_seedlot.id))
        self.assertEqual(response.status_code, 404)
