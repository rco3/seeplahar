# users/tests/test_partner_isolation.py

from users.models import Partner
from .base_isolation_test_case import BaseIsolationTest
from ..customer_context import CustomerContext


class PartnerIsolationTest(BaseIsolationTest):
    model = Partner
    app_name = 'users'

    def setUp(self):
        super().setUp()
        self.context = CustomerContext(self.customer1)
        self.context.__enter__()

    def tearDown(self):
        self.context.__exit__(None, None, None)
        super().tearDown()