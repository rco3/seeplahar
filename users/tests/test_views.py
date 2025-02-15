from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import Http404
from users.models import Customer, Partner
from django.core.exceptions import ValidationError
from users.middleware import CustomerMiddleware
from seeplahar.views.generic import GenericCreateView
from users.customer_context import CustomerContext, get_current_customer, clear_current_customer

User = get_user_model()


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name='Test Customer')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            customer=self.customer
        )
        self.partner = Partner.objects.create(
            name='Test Partner',
            customer=self.customer
        )

    def test_partner_create_view(self):
        self.client.login(username='testuser', password='testpass')
        data = {'name': 'New Partner'}
        response = self.client.post(reverse('users:partner_create'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertTrue(Partner.objects.filter(name='New Partner').exists())

    def test_partner_create_view_unauthenticated(self):
        # Don't log in
        data = {'name': 'New Partner'}
        response = self.client.post(reverse('users:partner_create'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertFalse(Partner.objects.filter(name='New Partner').exists())

    def test_partner_list_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partner')

    def test_partner_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(
            reverse('users:partner_detail', kwargs={'pk': self.partner.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partner')

    def test_partner_update_view(self):
        self.client.login(username='testuser', password='testpass')
        data = {'name': 'Updated Partner'}
        response = self.client.post(
            reverse('users:partner_update', kwargs={'pk': self.partner.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.name, 'Updated Partner')

    def test_partner_delete_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(
            reverse('users:partner_delete', kwargs={'pk': self.partner.pk})
        )
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertFalse(Partner.objects.filter(pk=self.partner.pk).exists())

    def test_cross_customer_access(self):
        # Create another customer and partner
        other_customer = Customer.objects.create(name='Other Customer')
        other_partner = Partner.objects.create(
            name='Other Partner',
            customer=other_customer
        )

        # Log in as original user
        self.client.login(username='testuser', password='testpass')

        # Try to access other customer's partner
        response = self.client.get(
            reverse('users:partner_detail', kwargs={'pk': other_partner.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_partner_access_wrong_customer(self):
        """Test partner access fails when user is from different customer"""
        # Create a second customer and user
        other_customer = Customer.objects.create(name='Other Customer')
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass',
            customer=other_customer
        )

        # Log in as the other user
        self.client.login(username='otheruser', password='testpass')

        # Try to access first customer's partner
        response = self.client.get(
            reverse('users:partner_detail', kwargs={'pk': self.partner.pk})
        )
        self.assertEqual(response.status_code, 404)  # Should not find partner

        # Try to create a partner (should create under other_customer)
        data = {'name': 'New Partner'}
        response = self.client.post(reverse('users:partner_create'), data)
        self.assertEqual(response.status_code, 302)  # Should succeed

        # Verify partner was created under correct customer
        new_partner = Partner.objects.get(name='New Partner')
        self.assertEqual(new_partner.customer, other_customer)
        self.assertNotEqual(new_partner.customer, self.customer)