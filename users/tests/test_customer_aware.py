from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from users.models import Customer, Partner
from users.customer_context import CustomerContext, get_current_customer, set_current_customer
from users.middleware import CustomerMiddleware
from seeplahar.views.generic import GenericCreateView
from django.http import HttpResponse
from django.core.exceptions import ValidationError

User = get_user_model()


class DummyView(GenericCreateView):
    model = Partner
    fields = ['name']
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse()


class CustomerAwareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.customer = Customer.objects.create(name="Test Customer")
        self.user = User.objects.create_user(username='testuser', password='12345', customer=self.customer)

    def test_customer_context(self):
        with CustomerContext(self.customer):
            self.assertEqual(get_current_customer(), self.customer)
        self.assertIsNone(get_current_customer())

    def test_customer_middleware(self):
        def get_response(request):
            # Check the customer right after it's set by the middleware
            self.assertEqual(get_current_customer(), self.customer)
            return HttpResponse()

        middleware = CustomerMiddleware(get_response)
        request = self.factory.get('/')
        request.user = self.user
        middleware(request)

        # After middleware completes, customer should be cleared
        self.assertIsNone(get_current_customer())

    def test_generic_create_view(self):
        view = DummyView.as_view()
        request = self.factory.post('/', {'name': 'Test Partner'})
        request.user = self.user
        with CustomerContext(self.customer):
            response = view(request)
        self.assertEqual(response.status_code, 200)
        partner = Partner.objects.get(name='Test Partner')
        self.assertEqual(partner.customer, self.customer)

    def test_create_user_without_customer(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(username='nocustomer', password='12345')

    # Add more tests as needed