"""
Farm API tests: Location, SeedLot, Planting, Harvest, HarvestContainer,
SeedlingBatch, Event — full CRUD via DRF + JWT.
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient
from django.utils import timezone

from farm.models import Location, SeedLot, Planting, Harvest, HarvestContainer, SeedlingBatch, Event
from farm.tests.base import FarmBaseTestCase


class FarmAPIBaseTestCase(FarmBaseTestCase):
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


# ── Location ─────────────────────────────────────────────────────────────────

class LocationAPITests(FarmAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/locations/')
        self.assertEqual(r.status_code, 200)
        names = [item['name'] for item in r.data['results']]
        self.assertIn('Hydroponics Bay 1', names)

    def test_create(self):
        r = self.api_client.post('/api/locations/', {'name': 'Greenhouse 3'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(Location.objects.filter(name='Greenhouse 3', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/locations/{self.location.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Hydroponics Bay 1')

    def test_update(self):
        r = self.api_client.patch(f'/api/locations/{self.location.id}/', {'name': 'Renamed Bay'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'Renamed Bay')

    def test_delete(self):
        loc = Location.objects.create(name='Temp', customer=self.customer)
        r = self.api_client.delete(f'/api/locations/{loc.id}/')
        self.assertEqual(r.status_code, 204)
        self.assertFalse(Location.objects.filter(id=loc.id).exists())

    def test_isolation(self):
        r = self.other_client().get('/api/locations/')
        names = [item['name'] for item in r.data['results']]
        self.assertNotIn('Hydroponics Bay 1', names)


# ── SeedLot ───────────────────────────────────────────────────────────────────

class SeedLotAPITests(FarmAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/seedlots/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.seedlot.id), ids)

    def test_create(self):
        data = {
            'variety': str(self.variety.id),
            'name': 'New Test Lot',
            'quantity': '50.00',
            'units': 'grams',
            'date_received': '2024-01-15',
        }
        r = self.api_client.post('/api/seedlots/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(SeedLot.objects.filter(name='New Test Lot', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/seedlots/{self.seedlot.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], self.seedlot.name)

    def test_update(self):
        r = self.api_client.patch(f'/api/seedlots/{self.seedlot.id}/', {'quantity': '200.00'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.seedlot.refresh_from_db()
        self.assertEqual(self.seedlot.quantity, 200)

    def test_delete(self):
        lot = SeedLot.objects.create(
            variety=self.variety, name='Delete Me', quantity=1, units='g', customer=self.customer
        )
        r = self.api_client.delete(f'/api/seedlots/{lot.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/seedlots/{self.seedlot.id}/')
        self.assertEqual(r.status_code, 404)


# ── Planting ──────────────────────────────────────────────────────────────────

class PlantingAPITests(FarmAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/plantings/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.planting.id), ids)

    def test_create(self):
        data = {
            'variety': str(self.variety.id),
            'date': '2024-03-01',
            'location': str(self.location.id),
            'status': 'growing',
            'quantity': 10,
        }
        r = self.api_client.post('/api/plantings/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/plantings/{self.planting.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/plantings/{self.planting.id}/', {'status': 'harvested'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.planting.refresh_from_db()
        self.assertEqual(self.planting.status, 'harvested')

    def test_delete(self):
        from users.customer_context import CustomerContext
        with CustomerContext(self.customer):
            p = Planting.objects.create(
                variety=self.variety, date='2024-04-01',
                location=self.location, status='growing', customer=self.customer,
            )
        r = self.api_client.delete(f'/api/plantings/{p.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/plantings/{self.planting.id}/')
        self.assertEqual(r.status_code, 404)


# ── Harvest ───────────────────────────────────────────────────────────────────

class HarvestAPITests(FarmAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/harvests/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.harvest.id), ids)

    def test_create(self):
        data = {
            'plants': [str(self.planting.id)],
            'date': '2024-04-01',
            'quantity': '30.00',
            'units': 'kg',
            'status': 'complete',
        }
        r = self.api_client.post('/api/harvests/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/harvests/{self.harvest.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update_status(self):
        r = self.api_client.patch(f'/api/harvests/{self.harvest.id}/', {'status': 'complete'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.harvest.refresh_from_db()
        self.assertEqual(self.harvest.status, 'complete')

    def test_delete(self):
        from users.customer_context import CustomerContext
        with CustomerContext(self.customer):
            h = Harvest.objects.create(date='2024-05-01', quantity=1, units='kg', customer=self.customer)
        r = self.api_client.delete(f'/api/harvests/{h.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/harvests/{self.harvest.id}/')
        self.assertEqual(r.status_code, 404)


# ── HarvestContainer ─────────────────────────────────────────────────────────

class HarvestContainerAPITests(FarmAPIBaseTestCase):
    def setUp(self):
        super().setUp()
        from users.customer_context import CustomerContext
        with CustomerContext(self.customer):
            self.container = HarvestContainer.objects.create(
                name='Bin A', container_type='bin', customer=self.customer
            )

    def test_list(self):
        r = self.api_client.get('/api/harvestcontainers/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.container.id), ids)

    def test_create(self):
        data = {'name': 'Basket 1', 'container_type': 'basket', 'status': 'available'}
        r = self.api_client.post('/api/harvestcontainers/', data, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(HarvestContainer.objects.filter(name='Basket 1', customer=self.customer).exists())

    def test_detail(self):
        r = self.api_client.get(f'/api/harvestcontainers/{self.container.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['name'], 'Bin A')

    def test_update(self):
        r = self.api_client.patch(f'/api/harvestcontainers/{self.container.id}/', {'status': 'in_use'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.container.refresh_from_db()
        self.assertEqual(self.container.status, 'in_use')

    def test_delete(self):
        from users.customer_context import CustomerContext
        with CustomerContext(self.customer):
            c = HarvestContainer.objects.create(name='Temp', customer=self.customer)
        r = self.api_client.delete(f'/api/harvestcontainers/{c.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/harvestcontainers/{self.container.id}/')
        self.assertEqual(r.status_code, 404)


# ── SeedlingBatch ─────────────────────────────────────────────────────────────

class SeedlingBatchAPITests(FarmAPIBaseTestCase):
    def test_list(self):
        r = self.api_client.get('/api/seedlingbatches/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.seedling_batch.id), ids)

    def test_create(self):
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        data = {
            'variety': str(self.variety.id),
            'date': '2024-03-15',
            'quantity': '25.00',
            'units': 'seedlings',
            'location': str(self.location.id),
            'source_content_type': seedlot_ct.id,
            'source_object_id': str(self.seedlot.id),
        }
        r = self.api_client.post('/api/seedlingbatches/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/seedlingbatches/{self.seedling_batch.id}/')
        self.assertEqual(r.status_code, 200)

    def test_update(self):
        r = self.api_client.patch(f'/api/seedlingbatches/{self.seedling_batch.id}/', {'quantity': '75.00'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.seedling_batch.refresh_from_db()
        self.assertEqual(self.seedling_batch.quantity, 75)

    def test_delete(self):
        from users.customer_context import CustomerContext
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        with CustomerContext(self.customer):
            sb = SeedlingBatch.objects.create(
                variety=self.variety, date='2024-06-01', quantity=10, units='seedlings',
                source_content_type=seedlot_ct, source_object_id=self.seedlot.id,
                customer=self.customer,
            )
        r = self.api_client.delete(f'/api/seedlingbatches/{sb.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/seedlingbatches/{self.seedling_batch.id}/')
        self.assertEqual(r.status_code, 404)


# ── Event ─────────────────────────────────────────────────────────────────────

class EventAPITests(FarmAPIBaseTestCase):
    def setUp(self):
        super().setUp()
        from users.customer_context import CustomerContext
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        with CustomerContext(self.customer):
            self.event = Event.objects.create(
                type='watering',
                date='2024-02-10',
                content_type=seedlot_ct,
                object_id=self.seedlot.id,
                customer=self.customer,
            )

    def test_list(self):
        r = self.api_client.get('/api/events/')
        self.assertEqual(r.status_code, 200)
        ids = [item['id'] for item in r.data['results']]
        self.assertIn(str(self.event.id), ids)

    def test_create(self):
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        data = {
            'type': 'fertilizing',
            'date': '2024-03-01',
            'content_type': seedlot_ct.id,
            'object_id': str(self.seedlot.id),
        }
        r = self.api_client.post('/api/events/', data, format='json')
        self.assertEqual(r.status_code, 201)

    def test_detail(self):
        r = self.api_client.get(f'/api/events/{self.event.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['type'], 'watering')

    def test_update(self):
        r = self.api_client.patch(f'/api/events/{self.event.id}/', {'type': 'pruning'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.type, 'pruning')

    def test_delete(self):
        from users.customer_context import CustomerContext
        seedlot_ct = ContentType.objects.get_for_model(SeedLot)
        with CustomerContext(self.customer):
            e = Event.objects.create(
                type='temp', date='2024-04-01',
                content_type=seedlot_ct, object_id=self.seedlot.id,
                customer=self.customer,
            )
        r = self.api_client.delete(f'/api/events/{e.id}/')
        self.assertEqual(r.status_code, 204)

    def test_isolation(self):
        r = self.other_client().get(f'/api/events/{self.event.id}/')
        self.assertEqual(r.status_code, 404)
