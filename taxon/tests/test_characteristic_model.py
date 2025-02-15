from django.db import IntegrityError, transaction
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from users.models import Customer
from taxon.models import Taxon, Variety, Characteristic, CharacteristicValue

User = get_user_model()


class CharacteristicModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Green Thumb Nursery")
        self.user = User.objects.create_user(
            username="plant_enthusiast",
            password="secret_garden",
            customer=self.customer
        )
        self.tomato_taxon = Taxon.objects.create(
            name="Tomato",
            species_name="Solanum lycopersicum",
            type=Taxon.VEGETABLE,
            customer=self.customer
        )
        self.beefsteak_variety = Variety.objects.create(
            name="Beefsteak",
            taxon=self.tomato_taxon,
            customer=self.customer
        )
        self.cherry_variety = Variety.objects.create(
            name="Cherry",
            taxon=self.tomato_taxon,
            customer=self.customer
        )

    def test_characteristic_creation(self):
        char = Characteristic.objects.create(
            name="Fruit Size",
            customer=self.customer
        )
        self.assertEqual(char.name, "Fruit Size")
        self.assertEqual(char.customer, self.customer)

    def test_characteristic_value_creation(self):
        char = Characteristic.objects.create(name="Fruit Size", customer=self.customer)
        char_value = CharacteristicValue.objects.create(
            characteristic=char,
            value="Large",
            taxon=self.tomato_taxon
        )
        self.assertEqual(char_value.value, "Large")
        self.assertEqual(char_value.taxon, self.tomato_taxon)

    def test_characteristic_variety_association(self):
        char = Characteristic.objects.create(name="Fruit Size", customer=self.customer)
        CharacteristicValue.objects.create(
            characteristic=char,
            value="Large",
            variety=self.beefsteak_variety
        )
        CharacteristicValue.objects.create(
            characteristic=char,
            value="Small",
            variety=self.cherry_variety
        )

        beefsteak_size = CharacteristicValue.objects.get(characteristic=char, variety=self.beefsteak_variety)
        cherry_size = CharacteristicValue.objects.get(characteristic=char, variety=self.cherry_variety)

        self.assertEqual(beefsteak_size.value, "Large")
        self.assertEqual(cherry_size.value, "Small")

    def test_characteristic_filtering(self):
        size_char = Characteristic.objects.create(name="Fruit Size", customer=self.customer)
        color_char = Characteristic.objects.create(name="Fruit Color", customer=self.customer)
        height_char = Characteristic.objects.create(name="Plant Height", customer=self.customer)

        size_chars = Characteristic.objects.filter(name__contains="Size")
        self.assertEqual(size_chars.count(), 1)
        self.assertEqual(size_chars.first().name, "Fruit Size")

    def test_characteristic_uniqueness(self):
        Characteristic.objects.create(name="Fruit Size", customer=self.customer)

        # Test that we can't create a duplicate characteristic for the same customer
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Characteristic.objects.create(name="Fruit Size", customer=self.customer)

        # Test that the same characteristic name can be used for a different customer
        other_customer = Customer.objects.create(name="Other Nursery")
        try:
            Characteristic.objects.create(name="Fruit Size", customer=other_customer)
        except IntegrityError:
            self.fail("Should be able to create characteristic with same name for different customer")

    def test_variety_characteristics(self):
        size_char = Characteristic.objects.create(name="Fruit Size", customer=self.customer)
        color_char = Characteristic.objects.create(name="Fruit Color", customer=self.customer)

        CharacteristicValue.objects.create(characteristic=size_char, value="Large", variety=self.beefsteak_variety)
        CharacteristicValue.objects.create(characteristic=color_char, value="Red", variety=self.beefsteak_variety)

        beefsteak_chars = CharacteristicValue.objects.filter(variety=self.beefsteak_variety)
        self.assertEqual(beefsteak_chars.count(), 2)
        self.assertIn("Large", beefsteak_chars.values_list('value', flat=True))
        self.assertIn("Red", beefsteak_chars.values_list('value', flat=True))

    def test_taxon_characteristics(self):
        leaf_char = Characteristic.objects.create(name="Leaf Type", customer=self.customer)
        growth_char = Characteristic.objects.create(name="Growth Habit", customer=self.customer)

        CharacteristicValue.objects.create(characteristic=leaf_char, value="Compound", taxon=self.tomato_taxon)
        CharacteristicValue.objects.create(characteristic=growth_char, value="Indeterminate", taxon=self.tomato_taxon)

        tomato_chars = CharacteristicValue.objects.filter(taxon=self.tomato_taxon)
        self.assertEqual(tomato_chars.count(), 2)
        self.assertIn("Compound", tomato_chars.values_list('value', flat=True))
        self.assertIn("Indeterminate", tomato_chars.values_list('value', flat=True))

    def test_characteristic_inheritance(self):
        taxon_char = Characteristic.objects.create(name="Leaf Type", customer=self.customer)
        CharacteristicValue.objects.create(characteristic=taxon_char, value="Compound", taxon=self.tomato_taxon)

        variety_char = Characteristic.objects.create(name="Fruit Size", customer=self.customer)
        CharacteristicValue.objects.create(characteristic=variety_char, value="Large", variety=self.beefsteak_variety)

        # Check that the variety has its own characteristics
        variety_chars = CharacteristicValue.objects.filter(variety=self.beefsteak_variety)
        self.assertIn("Large", variety_chars.values_list('value', flat=True))

        # Check that we can access the variety's taxon characteristics
        taxon_chars = CharacteristicValue.objects.filter(taxon=self.tomato_taxon)
        self.assertIn("Compound", taxon_chars.values_list('value', flat=True))

    def test_characteristic_precedence(self):
        color_char = Characteristic.objects.create(name="Color", customer=self.customer)

        # Assign red color to tomato taxon
        CharacteristicValue.objects.create(characteristic=color_char, value="Red", taxon=self.tomato_taxon)

        # Assign yellow color to cherry tomato variety
        CharacteristicValue.objects.create(characteristic=color_char, value="Yellow", variety=self.cherry_variety)

        # Helper function to get characteristic value
        def get_color(obj):
            if isinstance(obj, Variety):
                color_value = CharacteristicValue.objects.filter(characteristic=color_char, variety=obj).first()
                if color_value:
                    return color_value.value
                return get_color(obj.taxon)
            elif isinstance(obj, Taxon):
                color_value = CharacteristicValue.objects.filter(characteristic=color_char, taxon=obj).first()
                return color_value.value if color_value else None

        # Check taxon color
        self.assertEqual(get_color(self.tomato_taxon), "Red")

        # Check cherry variety color (should be Yellow, overriding the taxon's Red)
        self.assertEqual(get_color(self.cherry_variety), "Yellow")

        # Check beefsteak variety color (should inherit Red from the taxon)
        self.assertEqual(get_color(self.beefsteak_variety), "Red")