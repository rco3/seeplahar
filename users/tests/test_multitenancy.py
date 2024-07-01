# users/tests/test_multitenancy.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import Customer, Partner, ContactInfoType
from taxon.models import Taxon
from users.utils import create_user_with_email

User = get_user_model()


class MultiTenancyTest(TestCase):
    def setUp(self):
        print("\n--- Setup ---")
        self.customer1 = Customer.objects.create(name="Customer 1")
        self.customer2 = Customer.objects.create(name="Customer 2")

        self.initial_contact_type_count = ContactInfoType.objects.count()
        print(f"Initial ContactInfoType count: {self.initial_contact_type_count}")

        self.user1 = create_user_with_email('user1', 'user1@example.com', 'password', self.customer1)
        self.user2 = create_user_with_email('user2', 'user2@example.com', 'password', self.customer2)

        self.partner1 = Partner.objects.create(name="Partner 1", customer=self.customer1)
        self.partner2 = Partner.objects.create(name="Partner 2", customer=self.customer2)

        # Remove these lines as they're creating additional ContactInfoTypes
        self.contact_type1 = ContactInfoType.objects.create(name="Type 1", customer=self.customer1)
        self.contact_type2 = ContactInfoType.objects.create(name="Type 2", customer=self.customer2)

        self.taxon1 = Taxon.objects.create(name="tomato", species_name='solanum lycopersicum', type='Vegetable',
                                           description="tomato description", customer=self.customer1)
        self.taxon2 = Taxon.objects.create(name="watermelon", species_name='citrullus lanatus', type='Fruit',
                                           description="watermelon description", customer=self.customer2)

        print(f"Final ContactInfoType count: {ContactInfoType.objects.count()}")
        print("--- End Setup ---")

    def test_contact_info_type_creation(self):
        print("\n--- test_contact_info_type_creation ---")
        new_contact_type_count = ContactInfoType.objects.count() - self.initial_contact_type_count
        print(f"New ContactInfoType count: {new_contact_type_count}")

        for contact_type in ContactInfoType.objects.all():
            print(f"ContactInfoType: {contact_type.name}, Customer: {contact_type.customer.name}")

        self.assertEqual(new_contact_type_count, 4, "Expected 2 new ContactInfoTypes (one for each user)")

        # Verify that the new ContactInfoTypes are associated with the correct customers
        user1_contact_types = ContactInfoType.objects.filter(customer=self.customer1)
        user2_contact_types = ContactInfoType.objects.filter(customer=self.customer2)
        print(f"Customer 1 ContactInfoTypes: {user1_contact_types.count()}")
        print(f"Customer 2 ContactInfoTypes: {user2_contact_types.count()}")
        self.assertEqual(user1_contact_types.count(), 2, "Expected 1 ContactInfoType for Customer 1")
        self.assertEqual(user2_contact_types.count(), 2, "Expected 1 ContactInfoType for Customer 2")
        print("--- End test_contact_info_type_creation ---")

    def test_data_isolation(self):
        # Test Partner model
        self.assertEqual(Partner.objects.filter(customer=self.customer1).count(), 1)
        self.assertEqual(Partner.objects.filter(customer=self.customer2).count(), 1)
        self.assertNotEqual(Partner.objects.filter(customer=self.customer1).first(),
                            Partner.objects.filter(customer=self.customer2).first())

        # Test ContactInfoType model
        # Account for the additional ContactInfoType created during user creation
        expected_contact_type_count = 2  # 1 created explicitly + 1 from user creation
        self.assertEqual(ContactInfoType.objects.filter(customer=self.customer1).count(), expected_contact_type_count)
        self.assertEqual(ContactInfoType.objects.filter(customer=self.customer2).count(), expected_contact_type_count)
        self.assertNotEqual(ContactInfoType.objects.filter(customer=self.customer1).first(),
                            ContactInfoType.objects.filter(customer=self.customer2).first())

        # Test Taxon model
        self.assertEqual(Taxon.objects.filter(customer=self.customer1).count(), 1)
        self.assertEqual(Taxon.objects.filter(customer=self.customer2).count(), 1)
        self.assertNotEqual(Taxon.objects.filter(customer=self.customer1).first(),
                            Taxon.objects.filter(customer=self.customer2).first())

    def test_user_customer_association(self):
        self.assertEqual(self.user1.customer, self.customer1)
        self.assertEqual(self.user2.customer, self.customer2)
        self.assertNotEqual(self.user1.customer, self.user2.customer)