# users/middleware.py
from django.http import Http404


from django.utils.deprecation import MiddlewareMixin
from users.customer_context import set_current_customer, get_current_customer, clear_current_customer


class CustomerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # print(f"Middleware: Setting customer for user: {request.user.username}")
            set_current_customer(request.user.customer)
        else:
            # print("Middleware: No authenticated user, setting customer to None")
            set_current_customer(None)
        # print(f"Middleware: Customer context after setting: {get_current_customer()}")

    def process_response(self, request, response):
        # print(f"Middleware: Customer context before clearing: {get_current_customer()}")
        clear_current_customer()
        # print("Middleware: Customer context cleared")
        return response