# farm/tests/test_seedlot_views.py
from django.urls import reverse

from users.customer_context import CustomerContext

from .base import FarmBaseTestCase
from ..models import SeedLot


class SeedLotViewsTestCase(FarmBaseTestCase):
    def test_seedlot_list_view(self):
        self.login_test_user()
        response = self.client.get(reverse('farm:seedlot_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.variety.taxon.name)
        self.assertContains(response, self.seedlot.vendor)

    def test_seedlot_detail_view(self):
        self.login_test_user()
        response = self.client.get(reverse('farm:seedlot_detail', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Andorian Blue Pea Seeds Batch 1")

    def test_seedlot_create_view(self):
        self.login_test_user()
        data = {
            'variety': self.variety.id,
            'name': 'New SeedLot',
            'quantity': 200,
            'units': 'grams',
            'vendor': 'Federation Seeds'
        }
        response = self.client.post(reverse('farm:seedlot_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_seedlot = SeedLot.objects.get(name='New SeedLot')
        self.assertEqual(created_seedlot.customer, self.customer)

    def test_seedlot_update_view(self):
        self.login_test_user()
        data = {
            'variety': self.variety.id,
            'name': 'Updated SeedLot',
            'quantity': 150,
            'units': 'grams',
            'vendor': 'Starfleet Seed Cooperative'
        }
        response = self.client.post(reverse('farm:seedlot_update', args=[self.seedlot.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.seedlot.refresh_from_db()
        self.assertEqual(self.seedlot.name, 'Updated SeedLot')
        self.assertEqual(self.seedlot.customer, self.customer)

    def test_seedlot_delete_view(self):
        self.login_test_user()
        response = self.client.post(reverse('farm:seedlot_delete', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(SeedLot.objects.filter(id=self.seedlot.id).exists())

    def test_customer_isolation(self):
        # Create a seedlot for the other customer
        with CustomerContext(self.other_customer):
            other_seedlot = SeedLot.objects.create(
                variety=self.variety,
                name="Klingon Seeds",
                quantity=200,
                units="grams",
                vendor="Kronos Agro",
                customer=self.other_customer
            )

        # Test list view isolation
        self.login_test_user()
        response = self.client.get(reverse('farm:seedlot_list'))
        self.assertContains(response, self.seedlot.vendor)
        self.assertNotContains(response, "Kronos Agro")

        # Test can't access other customer's detail
        response = self.client.get(reverse('farm:seedlot_detail', args=[other_seedlot.id]))
        self.assertEqual(response.status_code, 404)

        # Test can't update other customer's seedlot
        data = {'name': 'Hacked Seedlot'}
        response = self.client.post(reverse('farm:seedlot_update', args=[other_seedlot.id]), data)
        self.assertEqual(response.status_code, 404)
        other_seedlot.refresh_from_db()
        self.assertEqual(other_seedlot.name, "Klingon Seeds")

        # Test can't delete other customer's seedlot
        response = self.client.post(reverse('farm:seedlot_delete', args=[other_seedlot.id]))
        self.assertEqual(response.status_code, 404)
        with CustomerContext(self.other_customer):
            self.assertTrue(SeedLot.objects.filter(id=other_seedlot.id).exists())

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('farm:seedlot_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn('login', response.url)

    def test_invalid_create_data(self):
        self.login_test_user()
        data = {
            'name': 'Invalid SeedLot',
            # Missing required variety
        }
        response = self.client.post(reverse('farm:seedlot_create'), data)
        self.assertEqual(response.status_code, 200)  # Returns to form
        self.assertFalse(SeedLot.objects.filter(name='Invalid SeedLot').exists())
