from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from taxon.models import Variety, Taxon
from farm.models import SeedLot
import uuid


class GenericDetailViewTests(TestCase):

    def setUp(self):
        # Create a Taxon
        self.taxon = Taxon.objects.create(
            id=uuid.uuid4(),
            name='Test Taxon',
            description='Test description for taxon'
        )

        # Create a Variety
        self.variety = Variety.objects.create(
            id=uuid.uuid4(),
            name='Test Variety',
            taxon=self.taxon,
            description='Test description for variety'
        )

        # Create SeedLot
        self.seedlot = SeedLot.objects.create(
            id=uuid.uuid4(),
            variety=self.variety,
            quantity=100,
            origin='Test SeedLot Origin',
            date_received=timezone.now()
        )

    def test_variety_detail_view(self):
        response = self.client.get(reverse('generic-detail', args=[str(self.variety.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taxon/variety_detail.html')
        self.assertContains(response, self.variety.name)
        self.assertContains(response, self.variety.description)

    def test_taxon_detail_view(self):
        response = self.client.get(reverse('generic-detail', args=[str(self.taxon.id)]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'taxon/taxon_detail.html')
        self.assertContains(response, self.taxon.name)
        self.assertContains(response, self.taxon.description)

    def test_404_for_invalid_uuid(self):
        invalid_uuid = uuid.uuid4()
        response = self.client.get(reverse('generic-detail', args=[str(invalid_uuid)]))
        self.assertEqual(response.status_code, 404)
