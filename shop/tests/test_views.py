
from django.template.defaultfilters import date as date_filter
from django.test import TestCase, Client
from django.urls import reverse
from shop.models import SeedPackage, ProducePackage, PlantPackage
from farm.models import SeedLot, Harvest, Planting
from taxon.models import Variety, Taxon
from users.models import Customer, User
from django.utils import timezone


class ShopViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Test Customer")
        self.user = User.objects.create_user(username="testuser", password="testpass", customer=self.customer)
        self.taxon = Taxon.objects.create(
            name="Test Taxon",
            species_name="Test Species",
            type=Taxon.VEGETABLE,
            customer=self.customer
        )
        self.variety = Variety.objects.create(
            name="Test Variety",
            taxon=self.taxon,
            customer=self.customer
        )
        self.seed_lot = SeedLot.objects.create(
            name="Test Seed Lot",
            variety=self.variety,
            quantity=100,
            units="seeds",
            customer=self.customer
        )
        self.planting = Planting.objects.create(
            variety=self.variety,
            date=timezone.now(),
            location="Test Location",
            status="growing",
            customer=self.customer
        )
        self.harvest = Harvest.objects.create(
            variety=self.variety,
            date=timezone.now(),
            quantity=50,
            units="kg",
            customer=self.customer
        )
        self.harvest.plants.add(self.planting)

        self.seed_package = SeedPackage.objects.create(
            seed_lot=self.seed_lot,
            quantity=10,
            quantity_units="seeds",
            date_packaged=timezone.now(),
            customer=self.customer
        )
        self.produce_package = ProducePackage.objects.create(
            harvest=self.harvest,
            quantity=5,
            quantity_units="kg",
            date_packaged=timezone.now(),
            customer=self.customer
        )
        self.plant_package = PlantPackage.objects.create(
            date_packaged=timezone.now(),
            quantity=3,
            customer=self.customer
        )
        self.plant_package.plants.add(self.planting)



    # List view tests
    def test_seed_package_list_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:seedpackage_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.seed_package.seed_lot.name)

    def test_produce_package_list_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:producepackage_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produce_package.date_packaged.strftime('%Y-%m-%d'))

    def test_plant_package_list_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:plantpackage_list'))
        self.assertEqual(response.status_code, 200)
        expected_date = date_filter(self.plant_package.date_packaged, "F j, Y")
        self.assertContains(response, expected_date)

    # Detail view tests
    def test_seed_package_detail_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:seedpackage_detail', args=[self.seed_package.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.seed_package.seed_lot.name)

    def test_produce_package_detail_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:producepackage_detail', args=[self.produce_package.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produce_package.date_packaged.strftime('%Y-%m-%d'))

    def test_plant_package_detail_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:plantpackage_detail', args=[self.plant_package.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.plant_package.date_packaged.strftime('%Y-%m-%d'))

    # Create view tests
    def test_seed_package_create_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'seed_lot': self.seed_lot.id,
            'quantity': 15,
            'quantity_units': 'seeds',
            'date_packaged': timezone.now().date(),
        }
        response = self.client.post(reverse('shop:seedpackage_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_package = SeedPackage.objects.get(seed_lot=self.seed_lot, quantity=15, quantity_units='seeds')
        self.assertEqual(created_package.quantity, 15)
        self.assertEqual(created_package.customer, self.customer)

    def test_produce_package_create_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'harvest': self.harvest.id,
            'quantity': 7,
            'quantity_units': 'kg',
            'date_packaged': timezone.now().date(),
        }
        response = self.client.post(reverse('shop:producepackage_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_package = ProducePackage.objects.get(harvest=self.harvest, quantity=7, quantity_units='kg')
        self.assertEqual(created_package.customer, self.customer)
        self.assertEqual(created_package.quantity, 7)

    def test_plant_package_create_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'quantity': 5,
            'date_packaged': timezone.now().date(),
            'plants': [self.planting.id],
        }
        response = self.client.post(reverse('shop:plantpackage_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        created_package = PlantPackage.objects.get(quantity=5, date_packaged=timezone.now().date())
        self.assertEqual(created_package.quantity, 5)
        self.assertEqual(created_package.date_packaged, timezone.now().date())
        self.assertEqual(created_package.plants.count(), 1)
        self.assertEqual(created_package.customer, self.customer)

    # Update view tests
    def test_seed_package_update_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'seed_lot': self.seed_lot.id,
            'quantity': 20,
            'quantity_units': 'seeds',
            'date_packaged': timezone.now().date(),
        }
        response = self.client.post(reverse('shop:seedpackage_update', args=[self.seed_package.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.seed_package.refresh_from_db()
        self.assertEqual(self.seed_package.quantity, 20)

    def test_produce_package_update_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'harvest': self.harvest.id,
            'quantity': 8,
            'quantity_units': 'kg',
            'date_packaged': timezone.now().date(),
        }
        response = self.client.post(reverse('shop:producepackage_update', args=[self.produce_package.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.produce_package.refresh_from_db()
        self.assertEqual(self.produce_package.quantity, 8)

    def test_plant_package_update_view(self):
        self.client.login(username="testuser", password="testpass")
        data = {
            'quantity': 4,
            'date_packaged': timezone.now().date(),
            'plants': [self.planting.id],
        }
        response = self.client.post(reverse('shop:plantpackage_update', args=[self.plant_package.id]), data)
        print(response.content.decode())
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.plant_package.refresh_from_db()
        self.assertEqual(self.plant_package.quantity, 4)

    # Delete view tests
    def test_seed_package_delete_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse('shop:seedpackage_delete', args=[self.seed_package.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(SeedPackage.objects.filter(id=self.seed_package.id).exists())

    def test_produce_package_delete_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse('shop:producepackage_delete', args=[self.produce_package.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(ProducePackage.objects.filter(id=self.produce_package.id).exists())

    def test_plant_package_delete_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(reverse('shop:plantpackage_delete', args=[self.plant_package.id]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(PlantPackage.objects.filter(id=self.plant_package.id).exists())

    # Additional tests for edge cases and permissions
    def test_unauthorized_access(self):
        # Create a new user without access to the customer's data
        other_customer = Customer.objects.create(name="Federation Labs")
        other_user = User.objects.create_user(username="otheruser", password="otherpass", customer=other_customer)
        self.client.login(username="otheruser", password="otherpass")
        response = self.client.get(reverse('shop:seedpackage_detail', args=[self.seed_package.id]))
        self.assertEqual(response.status_code, 404)  # Should not be able to view

    def test_customer_isolation(self):
        # Create a new customer and associated objects
        other_customer = Customer.objects.create(name="Other Customer")
        other_taxon = Taxon.objects.create(
            name="Andorian Blue Peas",
            species_name="Pisum andorii",
            type=Taxon.VEGETABLE,
            description="A vibrant blue pea from Andoria",
            customer=other_customer
        )
        other_variety = Variety.objects.create(
            name="Frost Resistant",
            taxon=other_taxon,
            description="Variety that can withstand extreme cold",
            customer=other_customer
        )
        other_seed_lot = SeedLot.objects.create(name="Other Seed Lot", customer=other_customer, variety=other_variety)

        other_seed_package = SeedPackage.objects.create(
            seed_lot=other_seed_lot,
            quantity=5,
            quantity_units="seeds",
            date_packaged=timezone.now(),
            customer=other_customer
        )

        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse('shop:seedpackage_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.seed_package.seed_lot.name)
        self.assertNotContains(response, other_seed_package.seed_lot.name)