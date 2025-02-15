from threading import local
from contextlib import ContextDecorator

_customer_context = local()

class CustomerContext(ContextDecorator):
    def __init__(self, customer):
        self.customer = customer
        self.old_customer = None

    def __enter__(self):
        self.old_customer = getattr(_customer_context, 'customer', None)
        _customer_context.customer = self.customer
        return self

    def __exit__(self, *exc):
        _customer_context.customer = self.old_customer

def get_current_customer():
    return getattr(_customer_context, 'customer', None)

def set_current_customer(customer):
    _customer_context.customer = customer

def clear_current_customer():
    if hasattr(_customer_context, 'customer'):
        del _customer_context.customer
