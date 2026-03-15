from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from farm.models import Planting, Event, Location
from taxon.models import Taxon, Variety
from users.customer_context import CustomerContext
from users.models import Customer
from django.utils import timezone

User = get_user_model()


class EventViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Starfleet Gardens")

        with CustomerContext(self.customer):
            self.user = User.objects.create_user(username="picard", password="earlgrey", customer=self.customer)
            self.taxon = Taxon.objects.create(
                name="Andorian Blue Peas",
                species_name="Pisum andorii",
                type=Taxon.VEGETABLE,
                description="A vibrant blue pea from Andoria",
                customer=self.customer
            )
            self.variety = Variety.objects.create(
                name="Frost Resistant",
                taxon=self.taxon,
                description="Variety that can withstand extreme cold",
                customer=self.customer
            )
            self.location = Location.objects.create(name="Hydroponics Bay 1", customer=self.customer)
            self.planting = Planting.objects.create(
                variety=self.variety,
                date=timezone.now(),
                location=self.location,
                status="growing",
                customer=self.customer
            )
            self.event = Event.objects.create(
                type="watering",
                date=timezone.now(),
                description="Watered Andorian Blue Peas",
                content_type=ContentType.objects.get_for_model(Planting),
                object_id=self.planting.id,
                customer=self.customer
            )

        self.client.login(username="picard", password="earlgrey")

    def test_event_create_view(self):
        data = {
            'type': 'fertilizing',
            'date': timezone.now().date(),
            'description': 'Fertilized Andorian Blue Peas',
            'related_item_type': 'planting',
            'related_item_id': str(self.planting.id),
        }
        response = self.client.post(reverse('farm:event_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_event = Event.objects.filter(description='Fertilized Andorian Blue Peas').first()
        self.assertIsNotNone(created_event)
        self.assertEqual(created_event.customer, self.customer)
        self.assertEqual(created_event.content_type, ContentType.objects.get_for_model(Planting))
        self.assertEqual(created_event.object_id, self.planting.id)

    def test_event_update_view(self):
        data = {
            'type': 'pruning',
            'date': timezone.now().date(),
            'description': 'Pruned Andorian Blue Peas',
            'related_item_type': 'planting',
            'related_item_id': str(self.planting.id),
        }
        response = self.client.post(reverse('farm:event_update', args=[self.event.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.event.refresh_from_db()
        self.assertEqual(self.event.type, 'pruning')
        self.assertEqual(self.event.description, 'Pruned Andorian Blue Peas')
        self.assertEqual(self.event.content_type, ContentType.objects.get_for_model(Planting))
        self.assertEqual(self.event.object_id, self.planting.id)

    def test_event_list_view(self):
        response = self.client.get(reverse('farm:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Watered Andorian Blue Peas")

    def test_event_detail_view(self):
        response = self.client.get(reverse('farm:event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Watered Andorian Blue Peas")

    def test_event_delete_view(self):
        response = self.client.post(reverse('farm:event_delete', args=[self.event.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())
