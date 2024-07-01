from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from users.models import Customer, ContactInfo, ContactInfoType, EmailAddress, Address, PhoneNumber, WebPresence
from users.utils import create_user_with_email

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name='Test Customer')
        self.contact_type = ContactInfoType.objects.create(name="Delivery", customer=self.customer)

        self.user = create_user_with_email(
            username='limetord',
            email='testuser@example.com',
            password='password123',
            customer=self.customer
        )

    def test_user_creation(self):
        print("User attributes:", dir(self.user))
        print("User dict:", self.user.__dict__)
        print("User email addresses:", EmailAddress.objects.filter(
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id
        ))

        self.assertEqual(self.user.username, 'limetord')

        # Check the EmailAddress
        email_address = EmailAddress.objects.filter(
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            is_primary=True
        ).first()
        self.assertIsNotNone(email_address, "No primary email address found")
        self.assertEqual(email_address.email, 'testuser@example.com')

        self.assertEqual(self.user.customer.name, 'Test Customer')

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, 'Test Customer')

    def test_create_contact_info(self):
        # Create an Address
        address = Address.objects.create(
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type,
            street='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.assertIsInstance(address, ContactInfo)
        self.assertEqual(address.customer, self.customer)
        self.assertEqual(address.content_object, self.user)

        # Create an EmailAddress
        email = EmailAddress.objects.create(
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type,
            email='contact@example.com'
        )
        self.assertIsInstance(email, ContactInfo)
        self.assertEqual(email.email, 'contact@example.com')

        # Create a PhoneNumber
        phone = PhoneNumber.objects.create(
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type,
            number='1234567890'
        )
        self.assertIsInstance(phone, ContactInfo)
        self.assertEqual(phone.number, '1234567890')

        # Create a WebPresence
        web = WebPresence.objects.create(
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type,
            url='https://example.com'
        )
        self.assertIsInstance(web, ContactInfo)
        self.assertEqual(web.url, 'https://example.com')

    def test_get_primary_email(self):
        primary_email = self.user.get_primary_email()
        self.assertEqual(primary_email, 'testuser@example.com')

        # Create a non-primary email
        EmailAddress.objects.create(
            customer=self.customer,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user.id,
            contact_function=self.contact_type,
            email='secondary@example.com',
            is_primary=False
        )

        # Ensure get_primary_email still returns the primary email
        self.assertEqual(self.user.get_primary_email(), 'testuser@example.com')