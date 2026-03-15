"""
Shop API tests: SeedPackage, ProducePackage, PlantPackage — full CRUD via DRF + JWT.
"""
from rest_framework.test import APIClient
from django.utils import timezone

from farm.tests.base import FarmBaseTestCase
from shop.models import SeedPackage, ProducePackage, PlantPackage
from users.customer_context import CustomerContext


class ShopAPIBaseTestCase(FarmBaseTestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        r = self.api_client.post('/api/auth/token/', {
            'username': 'picard', 'password': 'earlgrey',
        }, format='json')
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')

        # Create base packages
        with CustomerContext(self.customer):
            self.seed_package = SeedPackage.objects.create(
                seed_lot=self.seedlot,
                quantity=10,
                quantity_units='seeds',
                date_packaged=timezone.now().date(),
                customer=self.customer,
            )
            self.produce_package = ProducePackage.objects.create(
                harvest=self.harvest,
                quantity=5,
                quantity_units='kg',
                date_packaged=timezone.now().date(),
                customer=self.customer,
            )
            self.plant_package = PlantPackage.objects.create(
                date_packaged=timezone.now().date(),
                quantity=3,
                customer=self.customer,
            )
            self.plant_package.plants.add(self.planting)

    def other_client(self):
        client = APIClient()
        r = client.post('/api/auth/token/', {
            'username': 'worf', 'password': 'prune_juice',
        }, format='json')
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {r.data["access"]}')
        return client


class SeedPackageAPITests(ShopAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/seedpackages/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.seed_package.id), ids)

    def test_create(self):
        data = {
            'seed_lot': str(self.seedlot.id),
            'quantity': '20.00',
            'quantity_units': 'seeds',
            'date_packaged': str(timezone.now().date()),
        }
        r = self.api_client.post('/api/seedpackages/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(SeedPackage.objects.filter(quantity=20, customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/seedpackages/{self.seed_package.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/seedpackages/{self.seed_package.id}/', {'quantity': '15.00'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.seed_package.refresh_from_db()
        self.assertEqual(self.seed_package.quantity, 15)

    def test_delete(self):
        with CustomerContext(self.customer):
            sp = SeedPackage.objects.create(
                seed_lot=self.seedlot, quantity=1, quantity_units='seeds',
                date_packaged=timezone.now().date(), customer=self.customer,
            )
        r = self.api_client.delete(f'/api/seedpackages/{sp.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/seedpackages/{self.seed_package.id}/')
        self.assertEqual(r.status_code, 404)


class ProducePackageAPITests(ShopAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/producepackages/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.produce_package.id), ids)

    def test_create(self):
        data = {
            'harvest': str(self.harvest.id),
            'quantity': '8.00',
            'quantity_units': 'kg',
            'date_packaged': str(timezone.now().date()),
        }
        r = self.api_client.post('/api/producepackages/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/producepackages/{self.produce_package.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/producepackages/{self.produce_package.id}/', {'quantity': '6.00'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.produce_package.refresh_from_db()
        self.assertEqual(self.produce_package.quantity, 6)

    def test_delete(self):
        with CustomerContext(self.customer):
            pp = ProducePackage.objects.create(
                harvest=self.harvest, quantity=1, quantity_units='kg',
                date_packaged=timezone.now().date(), customer=self.customer,
            )
        r = self.api_client.delete(f'/api/producepackages/{pp.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/producepackages/{self.produce_package.id}/')
        self.assertEqual(r.status_code, 404)


class PlantPackageAPITests(ShopAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/plantpackages/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.plant_package.id), ids)

    def test_create(self):
        data = {
            'plants': [str(self.planting.id)],
            'date_packaged': str(timezone.now().date()),
            'quantity': 5,
        }
        r = self.api_client.post('/api/plantpackages/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/plantpackages/{self.plant_package.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/plantpackages/{self.plant_package.id}/', {'quantity': 4}, format='json')
        self.assertEqual(r.status_code, 200)
        self.plant_package.refresh_from_db()
        self.assertEqual(self.plant_package.quantity, 4)

    def test_delete(self):
        with CustomerContext(self.customer):
            pp = PlantPackage.objects.create(
                date_packaged=timezone.now().date(), quantity=1, customer=self.customer,
            )
        r = self.api_client.delete(f'/api/plantpackages/{pp.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/plantpackages/{self.plant_package.id}/')
        self.assertEqual(r.status_code, 404)
