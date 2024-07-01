from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from users.models import Customer, EmailAddress, ContactInfoType
from users.utils import create_user_with_email

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer")
        self.contact_type = ContactInfoType.objects.create(name="Test Type", customer=self.customer)

    def test_user_creation(self):
        user = create_user_with_email(
            username="testuser",
            email="testuser@example.com",
            password="testpass",
            customer=self.customer
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.customer, self.customer)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_get_primary_email(self):
        user = create_user_with_email(
            username="testuser",
            email="primary@example.com",
            password="testpass",
            customer=self.customer
        )
        EmailAddress.objects.create(
            email="secondary@example.com",
            is_primary=False,
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=user.id,
            contact_function=self.contact_type
        )
        self.assertEqual(user.get_primary_email(), "primary@example.com")