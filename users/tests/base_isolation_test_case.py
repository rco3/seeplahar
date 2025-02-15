from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.contrib.auth import get_user_model
from users.models import Customer
from users.middleware import CustomerMiddleware
from seeplahar.views.generic import GenericListView, GenericDetailView, GenericCreateView, GenericUpdateView, \
    GenericDeleteView
from users.customer_context import get_current_customer, set_current_customer
import logging

User = get_user_model()


class BaseIsolationTest(TestCase):
    model = None  # Set this in subclasses
    app_name = None  # Set this in subclasses

    @classmethod
    def setUpClass(cls):
        if cls is BaseIsolationTest:
            return
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        if cls is BaseIsolationTest:
            return
        super().tearDownClass()

    def setUp(self):
        if self.__class__ is BaseIsolationTest:
            self.skipTest("Skip BaseIsolationTest, it's a base class")

        self.factory = RequestFactory()

        # Create two customers
        self.customer1 = Customer.objects.create(name='Test Customer 1')
        self.customer2 = Customer.objects.create(name='Test Customer 2')

        # Create a user for each customer
        self.user1 = User.objects.create_user(username='testuser1', password='testpass1', customer=self.customer1)
        self.user2 = User.objects.create_user(username='testuser2', password='testpass2', customer=self.customer2)

        # Create an object for each customer
        self.object1 = self.model.objects.create(name='Test Object 1', customer=self.customer1)
        self.object2 = self.model.objects.create(name='Test Object 2', customer=self.customer2)

    def apply_middleware(self, request):
        middleware = CustomerMiddleware(lambda r: None)
        print(f"BaseIsolationTest: Before middleware, current customer: {get_current_customer()}")
        middleware.process_request(request)
        print(f"BaseIsolationTest: After middleware process_request, current customer: {get_current_customer()}")
        # We don't call process_response here, as it should be called after the view

    def test_list_view_isolation(self):
        print("\nTesting list view isolation")
        request = self.factory.get(reverse(f'{self.app_name}:{self.model._meta.model_name}_list'))
        request.user = self.user1
        print(f"BaseIsolationTest: Set user to {request.user.username}, customer: {request.user.customer}")
        set_current_customer(self.user1.customer)
        self.apply_middleware(request)

        print(f"BaseIsolationTest: Before view, current customer: {get_current_customer()}")
        response = GenericListView.as_view(model=self.model)(request)
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Object 1')
        self.assertNotContains(response, 'Test Object 2')
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")
        middleware = CustomerMiddleware(lambda r: None)
        middleware.process_response(request, response)

    def test_detail_view_isolation(self):
        print("\nTesting detail view isolation")
        request = self.factory.get(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_detail', kwargs={'pk': self.object1.pk}))
        request.user = self.user1
        print(f"BaseIsolationTest: Set user to {request.user.username}, customer: {request.user.customer}")
        set_current_customer(self.user1.customer)
        self.apply_middleware(request)


        print(f"BaseIsolationTest: Before view, current customer: {get_current_customer()}")
        response = GenericDetailView.as_view(model=self.model)(request, pk=self.object1.pk)
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Object 1')

        request = self.factory.get(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_detail', kwargs={'pk': self.object2.pk}))
        request.user = self.user1
        set_current_customer(self.user1.customer)
        self.apply_middleware(request)

        print(f"BaseIsolationTest: Before view (other object), current customer: {get_current_customer()}")
        with self.assertRaises(Http404):
            GenericDetailView.as_view(model=self.model)(request, pk=self.object2.pk)
        print(f"BaseIsolationTest: After view (other object), current customer: {get_current_customer()}")
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")
        middleware = CustomerMiddleware(lambda r: None)
        middleware.process_response(request, response)

    def test_create_view_customer_assignment(self):
        data = {'name': 'New Object'}
        request = self.factory.post(reverse(f'{self.app_name}:{self.model._meta.model_name}_create'), data)
        request.user = self.user1
        set_current_customer(self.customer1)
        self.apply_middleware(request)

        response = GenericCreateView.as_view(model=self.model, fields=['name'])(request)
        self.assertEqual(response.status_code, 302)
        new_object = self.model.objects.get(name='New Object')
        self.assertEqual(new_object.customer, self.customer1)
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")
        middleware = CustomerMiddleware(lambda r: None)
        middleware.process_response(request, response)

    def test_update_view_isolation(self):
        # Test updating own object
        data = {'name': 'Updated Test Object'}
        request = self.factory.post(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_update', kwargs={'pk': self.object1.pk}), data)
        request.user = self.user1
        set_current_customer(self.customer1)
        self.apply_middleware(request)

        response = GenericUpdateView.as_view(model=self.model, fields=['name'])(request, pk=self.object1.pk)
        self.assertEqual(response.status_code, 302)
        self.object1.refresh_from_db()
        self.assertEqual(self.object1.name, 'Updated Test Object')

        # Test updating other customer's object
        request = self.factory.post(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_update', kwargs={'pk': self.object2.pk}), data)
        request.user = self.user1
        set_current_customer(self.customer1)
        self.apply_middleware(request)

        with self.assertRaises(Http404):
            GenericUpdateView.as_view(model=self.model, fields=['name'])(request, pk=self.object2.pk)
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")
        middleware = CustomerMiddleware(lambda r: None)
        middleware.process_response(request, response)

    def test_delete_view_isolation(self):
        print("\nTesting delete view isolation")
        print(f"Object1 ID: {self.object1.pk}, Customer: {self.object1.customer}")
        print(f"User1: {self.user1}, Customer: {self.user1.customer}")

        request = self.factory.post(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_delete', kwargs={'pk': self.object1.pk}))
        request.user = self.user1
        print(f"BaseIsolationTest: Set user to {request.user.username}, customer: {request.user.customer}")
        set_current_customer(self.user1.customer)
        self.apply_middleware(request)

        print(f"BaseIsolationTest: Before view, current customer: {get_current_customer()}")
        response = GenericDeleteView.as_view(model=self.model)(request, pk=self.object1.pk)
        print(f"BaseIsolationTest: After view, current customer: {get_current_customer()}")
        print(f"View called. Response status: {response.status_code}")

        if response.status_code == 302:  # Redirect status
            print("Delete view redirected (success)")
        elif response.status_code == 200:  # OK status
            print("Delete view returned OK status")
        else:
            print(f"Unexpected response status: {response.status_code}")

        object_exists = self.model.objects.filter(pk=self.object1.pk).exists()
        print(f"After view call. Object still exists: {object_exists}")
        self.assertFalse(object_exists, "The object should have been deleted")

        # Test deletion of other customer's object
        print("\nTesting deletion of other customer's object")
        request = self.factory.post(
            reverse(f'{self.app_name}:{self.model._meta.model_name}_delete', kwargs={'pk': self.object2.pk}))
        request.user = self.user1
        set_current_customer(self.user1.customer)
        self.apply_middleware(request)

        print(f"BaseIsolationTest: Before view (other object), current customer: {get_current_customer()}")
        with self.assertRaises(Http404):
            GenericDeleteView.as_view(model=self.model)(request, pk=self.object2.pk)
        print(f"BaseIsolationTest: After view (other object), current customer: {get_current_customer()}")

        self.assertTrue(self.model.objects.filter(pk=self.object2.pk).exists(),
                        "Other customer's object should not be deleted")

        middleware = CustomerMiddleware(lambda r: None)
        middleware.process_response(request, HttpResponse())  # Use a dummy response
        print(f"BaseIsolationTest: After middleware process_response, current customer: {get_current_customer()}")
