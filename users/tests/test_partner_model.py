from django.test import TestCase
from users.models import Customer, Partner

class PartnerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer")

    def test_partner_creation(self):
        partner = Partner.objects.create(name="Test Partner", customer=self.customer)
        self.assertEqual(partner.name, "Test Partner")
        self.assertEqual(partner.customer, self.customer)
        self.assertTrue(partner.is_active)

    def test_partner_str_representation(self):
        partner = Partner.objects.create(name="Test Partner", customer=self.customer)
        expected_str = f"Test Partner (Customer: {self.customer.name})"
        self.assertEqual(str(partner), expected_str)