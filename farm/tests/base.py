# farm/tests/base.py
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import Customer
from taxon.models import Taxon, Variety
from farm.models import SeedLot, Planting, Harvest, SeedlingBatch

User = get_user_model()


class FarmBaseTestCase(TestCase):
    def setUp(self):
        # Set up client
        self.client = Client()

        # Create customer
        self.customer = Customer.objects.create(name="Starfleet Gardens")
        self.other_customer = Customer.objects.create(name="Klingon Farms")

        # Create users
        self.user = User.objects.create_user(
            username="picard",
            password="earlgrey",
            customer=self.customer
        )
        self.other_user = User.objects.create_user(
            username="worf",
            password="prune_juice",
            customer=self.other_customer
        )

        # Create base taxonomy
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

        # Create base farm objects
        self.seedlot = SeedLot.objects.create(
            variety=self.variety,
            name="Andorian Blue Pea Seeds Batch 1",
            quantity=100,
            units="grams",
            customer=self.customer
        )

        self.planting = Planting.objects.create(
            variety=self.variety,
            date="2024-01-01",
            location="Hydroponics Bay 1",
            status="growing",
            customer=self.customer
        )

        self.seedling_batch = SeedlingBatch.objects.create(
            seed_lot=self.seedlot,
            date="2024-01-01",
            quantity=50,
            units="seedlings",
            status="germinating",
            customer=self.customer
        )

        self.harvest = Harvest.objects.create(
            date="2024-02-01",
            quantity=50,
            units="kg",
            description="First harvest of Andorian Blue Peas",
            customer=self.customer
        )
        self.harvest.plants.add(self.planting)

    def login_test_user(self):
        """Helper method to log in as the main test user"""
        return self.client.login(username="picard", password="earlgrey")

    def login_other_user(self):
        """Helper method to log in as the other customer's user"""
        return self.client.login(username="worf", password="prune_juice")