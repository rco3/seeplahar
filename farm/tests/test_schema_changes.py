"""
Tests for schema additions:
  - HarvestContainer model
  - Harvest.status and Harvest.container FK
  - Location FK on Planting, SeedlingBatch, SeedLot (replacing CharFields)
  - Event.operator FK
"""
from django.test import TestCase
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from farm.models import (
    HarvestContainer, Harvest, Planting, SeedlingBatch, SeedLot, Event, Location
)
from farm.tests.base import FarmBaseTestCase
from users.customer_context import CustomerContext
from users.models import Customer, User


class HarvestContainerModelTests(FarmBaseTestCase):

    def test_harvest_container_creation_defaults(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                name='Basket 04',
                container_type='basket',
                customer=self.customer,
            )
        self.assertEqual(container.status, 'available')
        self.assertEqual(container.container_type, 'basket')
        self.assertEqual(container.customer, self.customer)
        self.assertIsNone(container.location)

    def test_harvest_container_str_with_name(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                name='Basket 04',
                container_type='basket',
                customer=self.customer,
            )
        self.assertEqual(str(container), 'Basket 04')

    def test_harvest_container_str_without_name(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                container_type='bag',
                customer=self.customer,
            )
        # Should fall back to type + short UUID
        self.assertIn('Bag', str(container))

    def test_harvest_container_at_location(self):
        with CustomerContext(self.customer):
            location = Location.objects.create(
                name='Cold Storage', customer=self.customer
            )
            container = HarvestContainer.objects.create(
                name='Bin 01',
                container_type='bin',
                location=location,
                customer=self.customer,
            )
        self.assertEqual(container.location, location)

    def test_harvest_container_customer_isolation(self):
        with CustomerContext(self.customer):
            HarvestContainer.objects.create(
                name='Picard Basket', container_type='basket', customer=self.customer
            )
        with CustomerContext(self.other_customer):
            HarvestContainer.objects.create(
                name='Worf Basket', container_type='basket', customer=self.other_customer
            )
        with CustomerContext(self.customer):
            self.assertEqual(HarvestContainer.objects.count(), 1)
        with CustomerContext(self.other_customer):
            self.assertEqual(HarvestContainer.objects.count(), 1)

    def test_harvest_container_history_empty(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                name='Empty Basket', container_type='basket', customer=self.customer
            )
        self.assertEqual(list(container.history), [])

    def test_harvest_container_history_reconstructed_from_harvests(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                name='History Basket', container_type='basket', customer=self.customer
            )
            h1 = Harvest.objects.create(
                date='2024-01-01', quantity=10, units='kg',
                container=container, customer=self.customer
            )
            h2 = Harvest.objects.create(
                date='2024-02-01', quantity=20, units='kg',
                container=container, customer=self.customer
            )
        history = list(container.history)
        self.assertIn(h1, history)
        self.assertIn(h2, history)
        self.assertEqual(len(history), 2)


class HarvestStatusTests(FarmBaseTestCase):

    def test_harvest_status_defaults_to_in_progress(self):
        with CustomerContext(self.customer):
            harvest = Harvest.objects.create(
                date=timezone.now().date(), quantity=5, units='kg',
                customer=self.customer
            )
        self.assertEqual(harvest.status, 'in_progress')

    def test_harvest_placeholder_status(self):
        with CustomerContext(self.customer):
            harvest = Harvest.objects.create(
                date=timezone.now().date(), quantity=0, units='kg',
                status='placeholder', customer=self.customer
            )
        self.assertEqual(harvest.status, 'placeholder')

    def test_harvest_complete_status(self):
        with CustomerContext(self.customer):
            harvest = Harvest.objects.create(
                date=timezone.now().date(), quantity=50, units='kg',
                status='complete', customer=self.customer
            )
        self.assertEqual(harvest.status, 'complete')

    def test_harvest_container_assignment(self):
        with CustomerContext(self.customer):
            container = HarvestContainer.objects.create(
                name='Assigned Basket', container_type='basket',
                status='in_use', customer=self.customer
            )
            harvest = Harvest.objects.create(
                date=timezone.now().date(), quantity=15, units='kg',
                container=container, customer=self.customer
            )
        self.assertEqual(harvest.container, container)

    def test_harvest_container_nullable(self):
        with CustomerContext(self.customer):
            harvest = Harvest.objects.create(
                date=timezone.now().date(), quantity=10, units='kg',
                customer=self.customer
            )
        self.assertIsNone(harvest.container)


class LocationFKTests(FarmBaseTestCase):
    """Planting, SeedlingBatch, and SeedLot all get a Location FK."""

    def setUp(self):
        super().setUp()
        with CustomerContext(self.customer):
            self.rack = Location.objects.create(
                name='Tomato Rack 22', customer=self.customer
            )
            self.shelf = Location.objects.create(
                name='Shelf 3', parent=self.rack, customer=self.customer
            )
            self.tray = Location.objects.create(
                name='Tray #7', parent=self.shelf, customer=self.customer
            )

    def test_planting_location_fk(self):
        with CustomerContext(self.customer):
            planting = Planting.objects.create(
                variety=self.variety, date=timezone.now().date(),
                status='growing', location=self.tray, customer=self.customer
            )
        self.assertEqual(planting.location, self.tray)
        self.assertEqual(planting.location.name, 'Tray #7')

    def test_planting_location_nullable(self):
        with CustomerContext(self.customer):
            planting = Planting.objects.create(
                variety=self.variety, date=timezone.now().date(),
                status='growing', customer=self.customer
            )
        self.assertIsNone(planting.location)

    def test_seedling_batch_location_fk(self):
        with CustomerContext(self.customer):
            batch = SeedlingBatch.objects.create(
                variety=self.variety, date=timezone.now().date(),
                quantity=50, units='seedlings', location=self.tray,
                customer=self.customer
            )
        self.assertEqual(batch.location, self.tray)

    def test_seedling_batch_location_nullable(self):
        with CustomerContext(self.customer):
            batch = SeedlingBatch.objects.create(
                variety=self.variety, date=timezone.now().date(),
                quantity=20, units='seedlings', customer=self.customer
            )
        self.assertIsNone(batch.location)

    def test_seedlot_location_fk(self):
        with CustomerContext(self.customer):
            seedlot = SeedLot.objects.create(
                variety=self.variety, quantity=100, units='grams',
                location=self.rack, customer=self.customer
            )
        self.assertEqual(seedlot.location, self.rack)

    def test_seedlot_location_nullable(self):
        with CustomerContext(self.customer):
            seedlot = SeedLot.objects.create(
                variety=self.variety, quantity=50, units='seeds',
                customer=self.customer
            )
        self.assertIsNone(seedlot.location)

    def test_location_reverse_query_plantings(self):
        with CustomerContext(self.customer):
            p1 = Planting.objects.create(
                variety=self.variety, date=timezone.now().date(),
                status='growing', location=self.tray, customer=self.customer
            )
            p2 = Planting.objects.create(
                variety=self.variety, date=timezone.now().date(),
                status='growing', location=self.tray, customer=self.customer
            )
            p_elsewhere = Planting.objects.create(
                variety=self.variety, date=timezone.now().date(),
                status='growing', location=self.shelf, customer=self.customer
            )
        tray_plantings = list(self.tray.plantings.all())
        self.assertIn(p1, tray_plantings)
        self.assertIn(p2, tray_plantings)
        self.assertNotIn(p_elsewhere, tray_plantings)

    def test_location_hierarchy(self):
        self.assertEqual(self.tray.parent, self.shelf)
        self.assertEqual(self.shelf.parent, self.rack)
        self.assertIsNone(self.rack.parent)
        self.assertIn(self.tray, self.shelf.children.all())


class EventOperatorTests(FarmBaseTestCase):

    def test_event_with_operator(self):
        with CustomerContext(self.customer):
            event = Event.objects.create(
                type='watered',
                date=timezone.now().date(),
                content_type=ContentType.objects.get_for_model(Planting),
                object_id=self.planting.id,
                operator=self.user,
                customer=self.customer,
            )
        self.assertEqual(event.operator, self.user)

    def test_event_operator_nullable(self):
        with CustomerContext(self.customer):
            event = Event.objects.create(
                type='system_check',
                date=timezone.now().date(),
                content_type=ContentType.objects.get_for_model(Planting),
                object_id=self.planting.id,
                customer=self.customer,
            )
        self.assertIsNone(event.operator)

    def test_event_operator_str(self):
        with CustomerContext(self.customer):
            event = Event.objects.create(
                type='fertilized',
                date=timezone.now().date(),
                description='Lord Farquaad fertilized the tomatoes',
                content_type=ContentType.objects.get_for_model(Planting),
                object_id=self.planting.id,
                operator=self.user,
                customer=self.customer,
            )
        self.assertEqual(event.operator.username, 'picard')
