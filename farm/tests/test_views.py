from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from farm.models import SeedLot, Planting, Harvest, SeedlingBatch, Event
from taxon.models import Taxon, Variety
from users.models import Customer, Partner
from django.utils import timezone

User = get_user_model()

class FarmViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer1 = Customer.objects.create(name="Starfleet Gardens")
        self.customer2 = Customer.objects.create(name="Klingon Farms")
        self.user1 = User.objects.create_user(username="picard", password="earlgrey", customer=self.customer1)
        self.user2 = User.objects.create_user(username="worf", password="prune_juice", customer=self.customer2)

        self.taxon = Taxon.objects.create(
            name="Andorian Blue Peas",
            species_name="Pisum andorii",
            type=Taxon.VEGETABLE,
            description="A vibrant blue pea from Andoria",
            customer=self.customer1
        )
        self.variety = Variety.objects.create(
            name="Frost Resistant",
            taxon=self.taxon,
            description="Variety that can withstand extreme cold",
            customer=self.customer1
        )
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name="Andorian Blue Pea Seeds Batch 1",
            quantity=100,
            units="grams",
            customer=self.customer1
        )
        self.planting = Planting.objects.create(
            variety=self.variety,
            date=timezone.now(),
            location="Hydroponics Bay 1",
            status="growing",
            customer=self.customer1,
            source_content_type=ContentType.objects.get_for_model(SeedLot),
            source_object_id=self.seedlot.id
        )
        self.harvest = Harvest.objects.create(
            date=timezone.now(),
            quantity=50,
            units="kg",
            description="First harvest of Andorian Blue Peas",
            customer=self.customer1
        )
        self.harvest.plants.add(self.planting)

        self.seedling_batch = SeedlingBatch.objects.create(
            seed_lot=self.seedlot,
            date=timezone.now(),
            quantity=50,
            units="seedlings",
            status="germinating",
            customer=self.customer1
        )
        # self.event = Event.objects.create(
        #     type="watering",
        #     date=timezone.now(),
        #     description="Watered Andorian Blue Peas",
        #     customer=self.customer1
        # )

    def test_customer_isolation(self):
        # Create a planting for customer2
        Planting.objects.create(
            variety=self.variety,
            date=timezone.now(),
            location="Klingon Battle Cruiser Garden",
            status="growing",
            customer=self.customer2
        )

        # Test that user1 can only see their own plantings
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:planting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hydroponics Bay 1")
        self.assertNotContains(response, "Klingon Battle Cruiser Garden")

        # Test that user2 can only see their own plantings
        self.client.login(username="worf", password="prune_juice")
        response = self.client.get(reverse('farm:planting_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Klingon Battle Cruiser Garden")
        self.assertNotContains(response, "Hydroponics Bay 1")

    def test_unauthorized_access(self):
        self.client.login(username="worf", password="prune_juice")
        response = self.client.get(reverse('farm:seedlot_detail', args=[self.seedlot.id]))
        self.assertEqual(response.status_code, 404)  # Or 403, depending on your implementation

    def test_qr_code_generation(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:generate_qr', args=[self.planting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')

    # Test for IntakeView
    def test_intake_view(self):
        self.client.login(username="picard", password="earlgrey")
        response = self.client.get(reverse('farm:intake'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Intake")  # Assuming the word "Intake" is on the page