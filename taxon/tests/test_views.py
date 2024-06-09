from django.test import TestCase
from django.urls import reverse
from taxon.models import Taxon, Variety
import uuid

class TaxonViewTests(TestCase):

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

    def test_taxon_list_view(self):
        response = self.client.get(reverse('taxon:taxon-list', kwargs={'type': self.taxon.type}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Taxon')

    def test_taxon_detail_view(self):
        response = self.client.get(reverse('taxon:taxon-detail', args=[str(self.taxon.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Taxon')

    def test_variety_detail_view(self):
        response = self.client.get(reverse('taxon:variety-detail', args=[str(self.variety.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Variety')

    def test_variety_list_view(self):
        response = self.client.get(reverse('taxon:variety-list', kwargs={'type': self.taxon.type, 'taxon_id': str(self.taxon.pk)}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Variety')
