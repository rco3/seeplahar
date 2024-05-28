from django.test import TestCase
from django.urls import reverse
from .models import Taxon, Variety
import uuid

class TaxonViewTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )

    def test_taxon_list_view(self):
        response = self.client.get(reverse('taxon_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Taxon')

    def test_taxon_detail_view(self):
        response = self.client.get(reverse('taxon_detail', args=[str(self.taxon.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Taxon')

    def test_taxon_create_view(self):
        response = self.client.post(reverse('taxon_create'), {
            'name': 'New Taxon',
            'species_name': 'New Species',
            'type': Taxon.FRUIT,
            'description': 'New Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Taxon.objects.filter(name='New Taxon').exists())

    def test_taxon_update_view(self):
        response = self.client.post(reverse('taxon_update', args=[str(self.taxon.pk)]), {
            'name': 'Updated Taxon',
            'species_name': 'Updated Species',
            'type': Taxon.HERB,
            'description': 'Updated Description'
        })
        self.assertEqual(response.status_code, 302)
        self.taxon.refresh_from_db()
        self.assertEqual(self.taxon.name, 'Updated Taxon')

    def test_taxon_delete_view(self):
        response = self.client.post(reverse('taxon_delete', args=[str(self.taxon.pk)]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Taxon.objects.filter(pk=self.taxon.pk).exists())
