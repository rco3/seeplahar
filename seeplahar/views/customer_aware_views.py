from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.http import Http404

from users.customer_context import CustomerContext, get_current_customer


class CustomerAwareViewMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.customer or not get_current_customer():
            raise Http404("No valid customer context for this request")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter_by_current_customer()


class CustomerAwareFormMixin:
    def has_customer_field(self):
        return hasattr(self.model, 'customer')

    def form_valid(self, form):
        if self.has_customer_field():
            current_customer = get_current_customer()
            if not current_customer:
                raise ValidationError("No valid customer context for this request")
            form.instance.customer = current_customer
        return super().form_valid(form)

    def get_form_class(self):
        form_class = super().get_form_class()
        if self.has_customer_field() and 'customer' in form_class.base_fields:
            del form_class.base_fields['customer']
        return form_class
