from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import Organization, ContactInfo

class UserViewTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Test Organization')
        self.user = get_user_model().objects.create_user(
            username='limetord',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )
        self.client.login(username='limetord', password='password123')
        self.contact_info = ContactInfo.objects.create(
            type='delivery',
            email='contact@example.com',
            site_user=self.user
        )

    def test_siteuser_list_view(self):
        response = self.client.get(reverse('users:siteuser_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'limetord')

    def test_siteuser_detail_view(self):
        response = self.client.get(reverse('users:siteuser_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'limetord')

    def test_organization_list_view(self):
        response = self.client.get(reverse('users:organization_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Organization')

    def test_organization_detail_view(self):
        response = self.client.get(reverse('users:organization_detail', args=[self.organization.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Organization')
