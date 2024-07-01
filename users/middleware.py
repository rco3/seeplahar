from threading import local
import logging

logger = logging.getLogger(__name__)

_customer = local()

class CustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # logger.debug(f"CustomerMiddleware - User: {request.user}")
        if request.user.is_authenticated:
            _customer.value = request.user.customer
            # logger.debug(f"CustomerMiddleware - Setting customer: {_customer.value}")
        else:
            _customer.value = None
            # logger.debug("CustomerMiddleware - No authenticated user")
        response = self.get_response(request)
        return response

def get_current_customer():
    customer = getattr(_customer, 'value', None)
    # logger.debug(f"get_current_customer called - Returning: {customer}")
    return customer