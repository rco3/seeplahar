from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Customer, Partner
from django.template import Template, Context
from seeplahar.templatetags.custom_tags import getattribute

User = get_user_model()

class GetAttributeFilterTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Test Customer')
        self.partner = Partner.objects.create(name='Test Partner', customer=self.customer)

    def test_getattribute_filter(self):
        # Test normal attribute access
        self.assertEqual(getattribute(self.partner, 'name'), 'Test Partner')

        # Test accessing a related object
        self.assertEqual(getattribute(self.partner, 'customer'), self.customer)

        # Test non-existent attribute
        self.assertTrue(getattribute(self.partner, 'non_existent').startswith('AttributeError:'))

        # Test with string input
        self.assertTrue(getattribute('string', 'attr').startswith('Error: Received string'))

    def test_getattribute_in_template(self):
        template = Template('{% load custom_tags %}{{ partner|getattribute:"name" }}')
        context = Context({'partner': self.partner})
        rendered = template.render(context)
        self.assertEqual(rendered, 'Test Partner')

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name='Test Customer')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            customer=self.customer,
            is_staff=True
        )
        self.partner = Partner.objects.create(
            name='Test Partner',
            customer=self.customer
        )

    def test_partner_list_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partner')

    def test_user_list_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_user_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:user_detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_partner_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_detail', kwargs={'pk': self.partner.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Partner')

    # New tests for Create, Update, and Delete operations

    def test_user_create_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:user_create'))
        self.assertEqual(response.status_code, 200)

        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            # 'password2': 'newpassword123',
            'customer': self.customer.id
        }
        response = self.client.post(reverse('users:user_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_update_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:user_update', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, 200)

        data = {
            'username': 'updateduser',
            'customer': self.customer.id
        }
        response = self.client.post(reverse('users:user_update', kwargs={'pk': self.user.id}), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_user_delete_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:user_delete', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('users:user_delete', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_partner_create_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_create'))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'New Partner',
            'customer': self.customer.id
        }
        response = self.client.post(reverse('users:partner_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Partner.objects.filter(name='New Partner').exists())

    def test_partner_update_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_update', kwargs={'pk': self.partner.id}))
        self.assertEqual(response.status_code, 200)

        data = {
            'name': 'Updated Partner',
            'customer': self.customer.id
        }
        response = self.client.post(reverse('users:partner_update', kwargs={'pk': self.partner.id}), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.partner.refresh_from_db()
        self.assertEqual(self.partner.name, 'Updated Partner')

    def test_partner_delete_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('users:partner_delete', kwargs={'pk': self.partner.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('users:partner_delete', kwargs={'pk': self.partner.id}))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Partner.objects.filter(id=self.partner.id).exists())

    # Add similar tests for Customer model if needed