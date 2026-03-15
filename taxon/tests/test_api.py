"""
Taxon API tests: Taxon, Variety, Characteristic — full CRUD via DRF + JWT.
"""
from rest_framework.test import APIClient
from farm.tests.base import FarmBaseTestCase
from taxon.models import Taxon, Variety, Characteristic
from users.customer_context import CustomerContext


class TaxonAPIBaseTestCase(FarmBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        r = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')

    def other_client(self):
        client = APIClient()
        r = client.post('/api/auth/token/', {
            'username': 'worf', 'password': 'prune_juice',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')
        return client


class TaxonAPITests(TaxonAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/taxa/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.taxon.id), ids)

    def test_create(self):
        data = {
            'name': 'Bajoran Pepper',
            'species_name': 'Capsicum bajorum',
            'type': 'vegetable',
        }
        r = self.api_client.post('/api/taxa/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Taxon.objects.filter(name='Bajoran Pepper', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/taxa/{self.taxon.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Andorian Blue Peas')

    def test_update(self):
        r = self.api_client.patch(f'/api/taxa/{self.taxon.id}/', {'description': 'Updated desc'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.taxon.refresh_from_db()
        self.assertEqual(self.taxon.description, 'Updated desc')

    def test_delete(self):
        with CustomerContext(self.customer):
            t = Taxon.objects.create(
                name='Delete Me', species_name='Deletius sp', type='other', customer=self.customer
            )
        r = self.api_client.delete(f'/api/taxa/{t.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/taxa/{self.taxon.id}/')
        self.assertEqual(r.status_code, 404)


class VarietyAPITests(TaxonAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/varieties/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.variety.id), ids)

    def test_create(self):
        data = {
            'name': 'Cold Hardy',
            'taxon': str(self.taxon.id),
        }
        r = self.api_client.post('/api/varieties/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Variety.objects.filter(name='Cold Hardy', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/varieties/{self.variety.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/varieties/{self.variety.id}/', {'description': 'Very cold hardy'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.variety.refresh_from_db()
        self.assertEqual(self.variety.description, 'Very cold hardy')

    def test_delete(self):
        with CustomerContext(self.customer):
            v = Variety.objects.create(name='Temp Variety', taxon=self.taxon, customer=self.customer)
        r = self.api_client.delete(f'/api/varieties/{v.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/varieties/{self.variety.id}/')
        self.assertEqual(r.status_code, 404)


class CharacteristicAPITests(TaxonAPIBaseTestCase):
    def setUp(self):
        super().setUp()
        with CustomerContext(self.customer):
            self.char = Characteristic.objects.create(name='Flavor', customer=self.customer)

    def test_list(self):
        r = self.api_client.get('/api/characteristics/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.char.id), ids)

    def test_create(self):
        r = self.api_client.post('/api/characteristics/', {'name': 'Texture'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Characteristic.objects.filter(name='Texture', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/characteristics/{self.char.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Flavor')

    def test_update(self):
        r = self.api_client.patch(f'/api/characteristics/{self.char.id}/', {'name': 'Taste'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.char.refresh_from_db()
        self.assertEqual(self.char.name, 'Taste')

    def test_delete(self):
        with CustomerContext(self.customer):
            c = Characteristic.objects.create(name='Temp Char', customer=self.customer)
        r = self.api_client.delete(f'/api/characteristics/{c.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/characteristics/{self.char.id}/')
        self.assertEqual(r.status_code, 404)
