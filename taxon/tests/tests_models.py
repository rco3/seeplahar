from django.test import TestCase
from taxon.models import Taxon, Variety
import uuid


class TaxonModelTests(TestCase):

    def setUp(self):
        self.taxon = Taxon.objects.create(
            name='Test Taxon',
            species_name='Test Species',
            type=Taxon.VEGETABLE,
            description='Test Description'
        )

    def test_taxon_creation(self):
        self.assertEqual(self.taxon.name, 'Test Taxon')
        self.assertEqual(self.taxon.species_name, 'Test Species')
        self.assertEqual(self.taxon.type, Taxon.VEGETABLE)
        self.assertEqual(self.taxon.description, 'Test Description')

    def test_taxon_str_method(self):
        self.assertEqual(str(self.taxon), 'Test Taxon')

    def test_taxon_update(self):
        self.taxon.name = 'Updated Taxon'
        self.taxon.save()
        self.assertEqual(self.taxon.name, 'Updated Taxon')

    def test_taxon_deletion(self):
        taxon_id = self.taxon.id
        self.taxon.delete()
        self.assertFalse(Taxon.objects.filter(id=taxon_id).exists())


class VarietyModelTests(TestCase):

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

    def test_variety_creation(self):
        self.assertEqual(self.variety.name, 'Test Variety')
        self.assertEqual(self.variety.taxon, self.taxon)
        self.assertEqual(self.variety.description, 'Test Variety Description')

    def test_variety_str_method(self):
        self.assertEqual(str(self.variety), 'Test Variety')

    def test_variety_update(self):
        self.variety.name = 'Updated Variety'
        self.variety.save()
        self.assertEqual(self.variety.name, 'Updated Variety')

    def test_variety_deletion(self):
        variety_id = self.variety.id
        self.variety.delete()
        self.assertFalse(Variety.objects.filter(id=variety_id).exists())
