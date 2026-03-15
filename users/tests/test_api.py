"""
Users API tests: Partner — full CRUD via DRF + JWT.
"""
from rest_framework.test import APIClient
from farm.tests.base import FarmBaseTestCase
from users.models import Partner
from users.customer_context import CustomerContext


class PartnerAPITests(FarmBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        r = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')

        with CustomerContext(self.customer):
            self.partner = Partner.objects.create(name='Vulcan Botanicals', customer=self.customer)

    def other_client(self):
        client = APIClient()
        r = client.post('/api/auth/token/', {
            'username': 'worf', 'password': 'prune_juice',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')
        return client

    def test_list(self):
        r = self.api_client.get('/api/partners/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.partner.id), ids)

    def test_create(self):
        data = {'name': 'Romulan Seeds Inc'}
        r = self.api_client.post('/api/partners/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Partner.objects.filter(name='Romulan Seeds Inc', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/partners/{self.partner.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Vulcan Botanicals')

    def test_update(self):
        r = self.api_client.patch(f'/api/partners/{self.partner.id}/', {'name': 'Vulcan Bio'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.name, 'Vulcan Bio')

    def test_delete(self):
        with CustomerContext(self.customer):
            p = Partner.objects.create(name='Temp Partner', customer=self.customer)
        r = self.api_client.delete(f'/api/partners/{p.id}/')
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Partner.objects.filter(id=p.id).exists())

    def test_isolation(self):
        r = self.other_client().get(f'/api/partners/{self.partner.id}/')
        self.assertEqual(r.status_code, 404)
