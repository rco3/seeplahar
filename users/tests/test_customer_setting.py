"""Tests for CustomerSetting model."""
from django.test import TestCase
from django.db import IntegrityError

from users.models import Customer, CustomerSetting


class CustomerSettingTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name='Starfleet Gardens')
        self.other_customer = Customer.objects.create(name='Klingon Farms')

    def test_create_setting(self):
        setting = CustomerSetting.objects.create(
            customer=self.customer, key='dedup_window_seconds', value='300'
        )
        self.assertEqual(setting.key, 'dedup_window_seconds')
        self.assertEqual(setting.value, '300')
        self.assertEqual(setting.customer, self.customer)

    def test_str(self):
        setting = CustomerSetting.objects.create(
            customer=self.customer, key='some_key', value='some_value'
        )
        self.assertIn('some_key', str(setting))

    def test_unique_per_customer_key(self):
        CustomerSetting.objects.create(
            customer=self.customer, key='dedup_window_seconds', value='300'
        )
        with self.assertRaises(IntegrityError):
            CustomerSetting.objects.create(
                customer=self.customer, key='dedup_window_seconds', value='600'
            )

    def test_same_key_allowed_for_different_customers(self):
        CustomerSetting.objects.create(
            customer=self.customer, key='dedup_window_seconds', value='300'
        )
        # Should not raise
        CustomerSetting.objects.create(
            customer=self.other_customer, key='dedup_window_seconds', value='60'
        )
        self.assertEqual(
            CustomerSetting.objects.filter(key='dedup_window_seconds').count(), 2
        )

    def test_get_returns_value(self):
        CustomerSetting.objects.create(
            customer=self.customer, key='dedup_window_seconds', value='300'
        )
        result = CustomerSetting.get(self.customer, 'dedup_window_seconds')
        self.assertEqual(result, '300')

    def test_get_returns_default_when_missing(self):
        result = CustomerSetting.get(self.customer, 'nonexistent_key', default='42')
        self.assertEqual(result, '42')

    def test_get_returns_none_default_when_missing_and_no_default(self):
        result = CustomerSetting.get(self.customer, 'nonexistent_key')
        self.assertIsNone(result)

    def test_set_creates_new_setting(self):
        CustomerSetting.set(self.customer, 'dedup_window_seconds', 300)
        self.assertEqual(
            CustomerSetting.get(self.customer, 'dedup_window_seconds'), '300'
        )

    def test_set_updates_existing_setting(self):
        CustomerSetting.objects.create(
            customer=self.customer, key='dedup_window_seconds', value='300'
        )
        CustomerSetting.set(self.customer, 'dedup_window_seconds', 600)
        self.assertEqual(
            CustomerSetting.get(self.customer, 'dedup_window_seconds'), '600'
        )
        self.assertEqual(
            CustomerSetting.objects.filter(
                customer=self.customer, key='dedup_window_seconds'
            ).count(), 1
        )

    def test_settings_isolated_per_customer(self):
        CustomerSetting.set(self.customer, 'dedup_window_seconds', 300)
        CustomerSetting.set(self.other_customer, 'dedup_window_seconds', 60)
        self.assertEqual(
            CustomerSetting.get(self.customer, 'dedup_window_seconds'), '300'
        )
        self.assertEqual(
            CustomerSetting.get(self.other_customer, 'dedup_window_seconds'), '60'
        )
