from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from farm.models import SeedLot
from taxon.models import Taxon, Variety
from users.models import Customer


User = get_user_model()


class LabelAccessTests(TestCase):
    def setUp(self):
        self.customer1 = Customer.objects.create(name='Alpha Farm')
        self.customer2 = Customer.objects.create(name='Beta Farm')

        self.user1 = User.objects.create_user(
            username='alpha_user',
            password='pass123',
            customer=self.customer1
        )
        self.user2 = User.objects.create_user(
            username='beta_user',
            password='pass123',
            customer=self.customer2
        )

        self.taxon1 = Taxon.objects.create(
            name='Tomato',
            species_name='Solanum lycopersicum',
            type=Taxon.VEGETABLE,
            customer=self.customer1
        )
        self.variety1 = Variety.objects.create(
            name='Alpha Tomato',
            taxon=self.taxon1,
            customer=self.customer1
        )
        self.seedlot1 = SeedLot.objects.create(
            variety=self.variety1,
            vendor='Alpha Seeds',
            customer=self.customer1
        )

        self.taxon2 = Taxon.objects.create(
            name='Pepper',
            species_name='Capsicum annuum',
            type=Taxon.VEGETABLE,
            customer=self.customer2
        )
        self.variety2 = Variety.objects.create(
            name='Beta Pepper',
            taxon=self.taxon2,
            customer=self.customer2
        )
        self.seedlot2 = SeedLot.objects.create(
            variety=self.variety2,
            vendor='Beta Seeds',
            customer=self.customer2
        )

    def test_label_pdf_requires_login(self):
        url = reverse('labels:label_pdf', args=['farm', 'seedlot', self.seedlot1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_label_pdf_scoped_to_customer(self):
        self.client.login(username='alpha_user', password='pass123')
        url = reverse('labels:label_pdf', args=['farm', 'seedlot', self.seedlot1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_label_pdf_blocks_other_customer(self):
        self.client.login(username='alpha_user', password='pass123')
        url = reverse('labels:label_pdf', args=['farm', 'seedlot', self.seedlot2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_generate_qr_blocks_other_customer(self):
        self.client.login(username='alpha_user', password='pass123')
        own_url = reverse('labels:generate_qr', args=[self.seedlot1.id])
        other_url = reverse('labels:generate_qr', args=[self.seedlot2.id])

        own_response = self.client.get(own_url)
        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(own_response['Content-Type'], 'image/png')

        other_response = self.client.get(other_url)
        self.assertEqual(other_response.status_code, 404)
