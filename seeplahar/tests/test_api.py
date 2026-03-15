"""
Cross-cutting API tests: JWT authentication and the /api/resolve/ endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from farm.tests.base import FarmBaseTestCase
from farm.models import SeedLot


class JWTAuthTests(FarmBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()

    def test_obtain_token(self):
        response = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_refresh_token(self):
        r = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        refresh = r.data['refresh']
        r2 = self.api_client.post('/api/auth/token/refresh/', {'refresh': refresh}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('access', r2.data)

    def test_unauthenticated_request_rejected(self):
        response = self.api_client.get('/api/seedlots/')
        self.assertEqual(response.status_code, 401)

    def _auth_as(self, username, password):
        r = self.api_client.post('/api/auth/token/', {
            'username': username, 'password': password,
        }, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')

    def test_authenticated_request_succeeds(self):
        self._auth_as('picard', 'earlgrey')
        response = self.api_client.get('/api/seedlots/')
        self.assertEqual(response.status_code, 200)

    def test_customer_isolation_via_jwt(self):
        # Picard can see his seedlot; Worf cannot
        self._auth_as('picard', 'earlgrey')
        response = self.api_client.get('/api/seedlots/')
        ids = [item['id'] for item in response.data['results']]
        self.assertIn(str(self.seedlot.id), ids)

        self.api_client.credentials()
        self._auth_as('worf', 'prune_juice')
        response = self.api_client.get('/api/seedlots/')
        ids = [item['id'] for item in response.data['results']]
        self.assertNotIn(str(self.seedlot.id), ids)


class ResolveViewTests(FarmBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        r = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')

    def test_resolve_seedlot(self):
        response = self.api_client.get(f'/api/resolve/{self.seedlot.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'seedlot')
        self.assertEqual(response.data['id'], str(self.seedlot.id))
        self.assertIn('/api/seedlots/', response.data['api_url'])

    def test_resolve_planting(self):
        response = self.api_client.get(f'/api/resolve/{self.planting.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'planting')

    def test_resolve_harvest(self):
        response = self.api_client.get(f'/api/resolve/{self.harvest.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'harvest')

    def test_resolve_variety(self):
        response = self.api_client.get(f'/api/resolve/{self.variety.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'variety')

    def test_resolve_unknown_uuid_returns_404(self):
        import uuid
        response = self.api_client.get(f'/api/resolve/{uuid.uuid4()}/')
        self.assertEqual(response.status_code, 404)

    def test_resolve_requires_auth(self):
        client = APIClient()
        response = client.get(f'/api/resolve/{self.seedlot.id}/')
        self.assertEqual(response.status_code, 401)
