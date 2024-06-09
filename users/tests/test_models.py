from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Organization, ContactInfo


class UserModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Test Organization')
        self.user = get_user_model().objects.create_user(
            username='limetord',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )
        self.contact_info = ContactInfo.objects.create(
            type='delivery',
            email='contact@example.com',
            site_user=self.user
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'limetord')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertEqual(self.user.organization.name, 'Test Organization')

    def test_organization_creation(self):
        self.assertEqual(self.organization.name, 'Test Organization')

    def test_contact_info_creation(self):
        self.assertEqual(self.contact_info.type, 'delivery')
        self.assertEqual(self.contact_info.email, 'contact@example.com')
        self.assertEqual(self.contact_info.site_user.username, 'limetord')
