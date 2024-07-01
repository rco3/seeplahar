from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from users.models import Customer, ContactInfoType, EmailAddress, PhoneNumber, Address, WebPresence

User = get_user_model()

class ContactInfoModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass",
            customer=self.customer
        )
        self.contact_type = ContactInfoType.objects.create(name="Test Type", customer=self.customer)

    def test_email_address_creation(self):
        email = EmailAddress.objects.create(
            email="test@example.com",
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type
        )
        self.assertEqual(email.email, "test@example.com")
        self.assertEqual(email.customer, self.customer)
        self.assertEqual(email.content_object, self.user)
        self.assertEqual(str(email), f"{self.contact_type} - test@example.com")

    def test_phone_number_creation(self):
        phone = PhoneNumber.objects.create(
            number="1234567890",
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type
        )
        self.assertEqual(phone.number, "1234567890")
        self.assertEqual(phone.customer, self.customer)
        self.assertEqual(phone.content_object, self.user)
        self.assertEqual(str(phone), f"{self.contact_type} - 1234567890")

    def test_address_creation(self):
        address = Address.objects.create(
            street="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="12345",
            country="Test Country",
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type
        )
        self.assertEqual(address.street, "123 Test St")
        self.assertEqual(address.city, "Test City")
        self.assertEqual(address.state, "Test State")
        self.assertEqual(address.postal_code, "12345")
        self.assertEqual(address.country, "Test Country")
        self.assertEqual(address.customer, self.customer)
        self.assertEqual(address.content_object, self.user)
        expected_str = f"{self.contact_type} - 123 Test St, Test City, Test State 12345, Test Country"
        self.assertEqual(str(address), expected_str)

    def test_web_presence_creation(self):
        web = WebPresence.objects.create(
            url="https://example.com",
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type
        )
        self.assertEqual(web.url, "https://example.com")
        self.assertEqual(web.customer, self.customer)
        self.assertEqual(web.content_object, self.user)
        self.assertEqual(str(web), f"{self.contact_type} - https://example.com")