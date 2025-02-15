from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from taxon.models import Taxon, Characteristic, Variety
from users.models import Customer
from users.customer_context import get_current_customer, set_current_customer

User = get_user_model()

class TaxonViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Botany Bay")
        self.user = User.objects.create_user(username="khan", password="KHAAAAAN!", customer=self.customer)
        self.taxon = Taxon.objects.create(
            name="Ceti Alpha V Slug",
            species_name="Ceti alphus sluggus",
            type=Taxon.OTHER,
            description="A small creature that enters through the ears and wraps itself around the cerebral cortex.",
            customer=self.customer
        )

    def test_taxon_list_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:taxon_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ceti Alpha V Slug")

    def test_taxon_type_list_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:taxon_type_list', kwargs={'type': self.taxon.type}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ceti Alpha V Slug")

    def test_taxon_detail_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:taxon_detail', args=[str(self.taxon.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ceti Alpha V Slug")
        self.assertContains(response, "Ceti alphus sluggus")

    def test_taxon_create_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        data = {
            'name': 'Genesis Device',
            'species_name': 'Projectus genesium',
            'type': Taxon.OTHER,
            'description': 'A technology designed to reorganize matter on a planetary scale.',
        }
        response = self.client.post(reverse('taxon:taxon_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Taxon.objects.filter(name='Genesis Device').exists())

    def test_taxon_update_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        data = {
            'name': 'Ceti Alpha V Eel',
            'species_name': 'Ceti alphus eelus',
            'type': Taxon.OTHER,
            'description': 'Updated description for the creature.',
        }
        response = self.client.post(reverse('taxon:taxon_update', args=[str(self.taxon.pk)]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.taxon.refresh_from_db()
        self.assertEqual(self.taxon.name, 'Ceti Alpha V Eel')

    def test_taxon_delete_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.post(reverse('taxon:taxon_delete', args=[str(self.taxon.pk)]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Taxon.objects.filter(pk=self.taxon.pk).exists())

    def test_customer_isolation(self):
        other_customer = Customer.objects.create(name="Federation Labs")
        other_taxon = Taxon.objects.create(
            name="Tribble",
            species_name="Polygeminus grex",
            type=Taxon.OTHER,
            description="A small, furry creature that reproduces at an alarming rate.",
            customer=other_customer
        )

        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:taxon_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ceti Alpha V Slug")
        self.assertNotContains(response, "Tribble")



class VarietyViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Botany Bay")
        self.user = User.objects.create_user(username="khan", password="KHAAAAAN!", customer=self.customer)
        self.taxon = Taxon.objects.create(
            name="Ceti Alpha V Slug",
            species_name="Ceti alphus sluggus",
            type=Taxon.OTHER,
            description="A small creature that enters through the ears and wraps itself around the cerebral cortex.",
            customer=self.customer
        )
        self.variety = Variety.objects.create(
            name="Earworm",
            taxon=self.taxon,
            description="A particularly aggressive variety of the Ceti Alpha V Slug.",
            customer=self.customer
        )

    def test_variety_list_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:variety_list', kwargs={'type': self.taxon.type, 'taxon_id': self.taxon.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Earworm")

    def test_variety_detail_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.get(reverse('taxon:variety_detail', args=[str(self.variety.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Earworm")

    def test_variety_create_view(self):
        print("\n=== Starting Variety Create Test ===")

        # Login setup
        self.client.login(username="khan", password="KHAAAAAN!")

        # Prepare form data with correct through-model prefix
        data = {
            # Main form data
            'name': 'New Variety',
            'taxon': self.taxon.id,
            'description': 'A new variety of the Ceti Alpha V Slug.',

            # Formset management data using through-model naming convention
            'characteristicvalue_set-TOTAL_FORMS': '0',
            'characteristicvalue_set-INITIAL_FORMS': '0',
            'characteristicvalue_set-MIN_NUM_FORMS': '0',
            'characteristicvalue_set-MAX_NUM_FORMS': '1000',
        }

        # Enhanced debugging output
        print("\nFormset Configuration:")
        print(f"Using prefix: characteristicvalue_set")
        print(f"Management form data: {data}")

        response = self.client.post(reverse('taxon:variety_create'), data)
        print(f"\nResponse Information:")
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            self._print_form_errors(response)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Variety.objects.filter(name='New Variety').exists())

    def _print_form_errors(self, response):
        """Helper method for detailed form error reporting"""
        print("\nForm Validation Details:")
        if 'form' in response.context:
            print("Main Form Errors:")
            print(response.context['form'].errors or "None")

        if 'characteristic_formset' in response.context:
            formset = response.context['characteristic_formset']
            print("\nFormset Information:")
            print(f"Total Forms: {formset.total_form_count()}")
            print(f"Initial Forms: {formset.initial_form_count()}")
            print(f"Non-form Errors: {formset.non_form_errors()}")
            print("Form Errors:", [f.errors for f in formset.forms])

    def test_variety_update_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        data = {
            'name': 'Updated Earworm',
            'taxon': self.taxon.id,
            'description': 'An updated description for the Earworm variety.',
        }
        response = self.client.post(reverse('taxon:variety_update', args=[str(self.variety.pk)]), data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.variety.refresh_from_db()
        self.assertEqual(self.variety.name, 'Updated Earworm')

    def test_variety_delete_view(self):
        self.client.login(username="khan", password="KHAAAAAN!")
        response = self.client.post(reverse('taxon:variety_delete', args=[str(self.variety.pk)]))
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertFalse(Variety.objects.filter(pk=self.variety.pk).exists())

# class CharacteristicViewsTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.customer = Customer.objects.create(name="Botany Bay")
#         self.user = User.objects.create_user(username="khan", password="KHAAAAAN!", customer=self.customer)
#         self.taxon = Taxon.objects.create(
#             name="Ceti Alpha V Slug",
#             species_name="Ceti alphus sluggus",
#             type=Taxon.OTHER,
#             description="A small creature that enters through the ears and wraps itself around the cerebral cortex.",
#             customer=self.customer
#         )
#         self.variety = Variety.objects.create(
#             name="Earworm",
#             taxon=self.taxon,
#             description="A particularly aggressive variety of the Ceti Alpha V Slug.",
#             customer=self.customer
#         )
#         self.characteristic = Characteristic.objects.create(
#             name="Aggression Level",
#             value="Extreme",
#             customer=self.customer
#         )
#         self.characteristic.varieties.add(self.variety)
#
#     def test_characteristic_create_view(self):
#         self.client.login(username="khan", password="KHAAAAAN!")
#         data = {
#             'name': 'Size',
#             'value': 'Small',
#             'varieties': [self.variety.id],
#         }
#         response = self.client.post(reverse('taxon:characteristic_create'), data)
#         self.assertEqual(response.status_code, 302)  # Redirect on success
#         self.assertTrue(Characteristic.objects.filter(name='Size', value='Small').exists())
#
#     def test_characteristic_update_view(self):
#         self.client.login(username="khan", password="KHAAAAAN!")
#         data = {
#             'name': 'Aggression Level',
#             'value': 'Apocalyptic',
#             'varieties': [self.variety.id],
#         }
#         response = self.client.post(reverse('taxon:characteristic_update', args=[str(self.characteristic.pk)]), data)
#         self.assertEqual(response.status_code, 302)  # Redirect on success
#         self.characteristic.refresh_from_db()
#         self.assertEqual(self.characteristic.value, 'Apocalyptic')
#
#     def test_characteristic_delete_view(self):
#         self.client.login(username="khan", password="KHAAAAAN!")
#         response = self.client.post(reverse('taxon:characteristic_delete', args=[str(self.characteristic.pk)]))
#         self.assertEqual(response.status_code, 302)  # Redirect on success
#         self.assertFalse(Characteristic.objects.filter(pk=self.characteristic.pk).exists())
