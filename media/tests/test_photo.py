from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.contenttypes.models import ContentType
from users.models import Customer, User, Partner
from taxon.models import Variety, Taxon
from media.models import Photo
import uuid
import os


class PhotoModelTest(TestCase):
    def setUp(self):
        # Create test customers
        self.customer1 = Customer.objects.create(name='Galactic Gardens')
        self.customer2 = Customer.objects.create(name='Martian Meadows')

        # Create test users
        self.user1 = User.objects.create_user(
            username='gardener1',
            password='test123',
            customer=self.customer1
        )
        self.user2 = User.objects.create_user(
            username='gardener2',
            password='test123',
            customer=self.customer2
        )

        # Create test partners
        self.partner1 = Partner.objects.create(
            name='Seed Supplier 1',
            customer=self.customer1
        )
        self.partner2 = Partner.objects.create(
            name='Seed Supplier 2',
            customer=self.customer2
        )

        # Create test taxon and variety
        self.taxon = Taxon.objects.create(
            name='Test Tomato',
            species_name='Solanum test',
            type='vegetable',
            customer=self.customer1
        )

        self.variety = Variety.objects.create(
            name='Test Variety',
            taxon=self.taxon,
            customer=self.customer1
        )

        # Create a test image file
        self.image_content = b'fake image content'
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=self.image_content,
            content_type='image/jpeg'
        )

    def tearDown(self):
        # Clean up any created files
        for photo in Photo.objects.all():
            if photo.image and os.path.exists(photo.image.path):
                os.remove(photo.image.path)

    def test_photo_creation(self):
        photo = Photo.objects.create(
            image=self.test_image,
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )

        # Test basic attributes
        self.assertEqual(photo.customer, self.customer1)
        self.assertTrue(isinstance(photo.id, uuid.UUID))

        # Test upload path format
        expected_prefix = f"gala_{str(self.customer1.id)[-8:]}"
        # Use photo.image.name to get the relative path instead of image.path
        self.assertTrue(photo.image.name.startswith(f"photos/{expected_prefix}"))

    def test_generic_foreign_key_relationship(self):
        photo = Photo.objects.create(
            image=self.test_image,
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )

        # Test GFK relationship
        self.assertEqual(photo.content_object, self.variety)

    def test_m2m_relationships(self):
        # Test for Variety
        variety_photo = Photo.objects.create(
            image=self.test_image,
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )
        self.variety.photos.add(variety_photo)
        self.assertIn(variety_photo, self.variety.photos.all())
        self.assertIn(self.variety, variety_photo.varieties.all())

        # Test for User
        user_photo = Photo.objects.create(
            image=SimpleUploadedFile('user.jpg', b'content', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(User),
            object_id=self.user1.id
        )
        self.user1.photos.add(user_photo)
        self.assertIn(user_photo, self.user1.photos.all())
        self.assertIn(self.user1, user_photo.users.all())

        # Test for Partner
        partner_photo = Photo.objects.create(
            image=SimpleUploadedFile('partner.jpg', b'content', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Partner),
            object_id=self.partner1.id
        )
        self.partner1.photos.add(partner_photo)
        self.assertIn(partner_photo, self.partner1.photos.all())
        self.assertIn(self.partner1, partner_photo.partners.all())

        # Test for Customer
        customer_photo = Photo.objects.create(
            image=SimpleUploadedFile('customer.jpg', b'content', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Customer),
            object_id=self.customer1.id
        )
        self.customer1.photos.add(customer_photo)
        self.assertIn(customer_photo, self.customer1.photos.all())
        self.assertIn(self.customer1, customer_photo.customers.all())

    def test_customer_isolation(self):
        # Create photos for both customers
        photo1 = Photo.objects.create(
            image=self.test_image,
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )

        photo2 = Photo.objects.create(
            image=SimpleUploadedFile('test2.jpg', b'content2', content_type='image/jpeg'),
            customer=self.customer2,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )

        # Test customer-specific queries
        self.assertEqual(Photo.objects.filter(customer=self.customer1).count(), 1)
        self.assertEqual(Photo.objects.filter(customer=self.customer2).count(), 1)

        # Test that each customer can only see their own photos
        customer1_photos = Photo.objects.filter(customer=self.customer1)
        self.assertIn(photo1, customer1_photos)
        self.assertNotIn(photo2, customer1_photos)

    def test_multiple_photos_per_object(self):
        # Create multiple photos for one variety
        photo1 = Photo.objects.create(
            image=SimpleUploadedFile('photo1.jpg', b'content1', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )
        photo2 = Photo.objects.create(
            image=SimpleUploadedFile('photo2.jpg', b'content2', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )
        photo3 = Photo.objects.create(
            image=SimpleUploadedFile('photo3.jpg', b'content3', content_type='image/jpeg'),
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )

        self.variety.photos.add(photo1, photo2, photo3)

        # Check all photos are associated
        self.assertEqual(self.variety.photos.count(), 3)
        self.assertIn(photo1, self.variety.photos.all())
        self.assertIn(photo2, self.variety.photos.all())
        self.assertIn(photo3, self.variety.photos.all())

    def test_photo_shared_between_objects(self):
        # Create one photo
        shared_photo = Photo.objects.create(
            image=SimpleUploadedFile('shared.jpg', b'content', content_type='image/jpeg'),
            customer=self.customer1
        )

        # Share it between variety and partner
        self.variety.photos.add(shared_photo)
        self.partner1.photos.add(shared_photo)

        # Check photo is associated with both objects
        self.assertIn(shared_photo, self.variety.photos.all())
        self.assertIn(shared_photo, self.partner1.photos.all())

        # Check reverse relationships
        self.assertIn(self.variety, shared_photo.varieties.all())
        self.assertIn(self.partner1, shared_photo.partners.all())

    def test_delete_relationships(self):
        photo = Photo.objects.create(
            image=self.test_image,
            customer=self.customer1,
            content_type=ContentType.objects.get_for_model(Variety),
            object_id=self.variety.id
        )
        self.variety.photos.add(photo)

        # Store IDs for verification
        photo_id = photo.id
        variety_id = self.variety.id

        # Delete the variety and verify the photo still exists
        self.variety.delete()
        self.assertTrue(Photo.objects.filter(id=photo_id).exists())
        self.assertIsNone(Photo.objects.get(id=photo_id).content_object)

        # Create new variety and verify we can reassign the photo
        new_variety = Variety.objects.create(
            name='New Test Variety',
            taxon=self.taxon,
            customer=self.customer1
        )
        photo = Photo.objects.get(id=photo_id)
        photo.content_type = ContentType.objects.get_for_model(Variety)
        photo.object_id = new_variety.id
        photo.save()
        new_variety.photos.add(photo)

        self.assertEqual(photo.content_object, new_variety)
        self.assertIn(photo, new_variety.photos.all())