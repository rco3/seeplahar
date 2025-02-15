# seeplahar/views/generic.py

from django.apps import apps
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from users.customer_context import get_current_customer
from users.models import Customer
from .customer_aware_views import CustomerAwareViewMixin, CustomerAwareFormMixin
from .base import BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView
import sys
import logging


class GenericModelView:
    def dispatch(self, request, *args, **kwargs):
        self.app_name = self.model._meta.app_label
        self.model_name = self.model._meta.model_name  # This is the database-friendly name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_fields'] = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in self.model._meta.fields
        ]
        # For display in templates - these can have spaces
        context['model_verbose_name'] = self.model._meta.verbose_name
        context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural

        # For URL generation - these must not have spaces
        context['model_name'] = self.model_name  # From dispatch
        context['app_label'] = self.app_name

        # Generate URL names using self.model_name which is guaranteed no spaces
        base_name = f"{self.app_name}:{self.model_name}"
        context['list_url_name'] = f"{base_name}_list"
        context['detail_url_name'] = f"{base_name}_detail"
        context['create_url_name'] = f"{base_name}_create"
        context['update_url_name'] = f"{base_name}_update"
        context['delete_url_name'] = f"{base_name}_delete"

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.model != Customer:
            customer = get_current_customer()
            if customer:
                return queryset.filter(customer=customer)
            return queryset.none()
        return queryset

# seeplahar/views/generic.py


class GenericCreateView(CustomerAwareFormMixin, GenericModelView, BaseCreateView):
    pass

class GenericUpdateView(CustomerAwareFormMixin, GenericModelView, BaseUpdateView):
    pass

# Other views should use CustomerAwareViewMixin if they need to be customer-aware
class GenericListView(GenericModelView, BaseListView):
    template_name = 'base_list.html'

    def get_template_names(self):
        model_template = f"{self.app_name}/{self.model_name}_list.html"
        return [model_template, self.template_name]

class GenericDetailView(GenericModelView, BaseDetailView):
    pass

class GenericDeleteView(GenericModelView, BaseDeleteView):
    template_name = 'base_confirm_delete.html'

    def get_success_url(self):
        return reverse(f'{self.model._meta.app_label}:{self.model._meta.model_name}_list')

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset)
            logging.info(f"Object retrieved: {obj}, Customer: {obj.customer}")
            return obj
        except Http404:
            logging.error(f"Object not found. Current customer: {get_current_customer()}")
            raise

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Http404:
            logging.error(f"Delete failed. Object not found. Current customer: {get_current_customer()}")
            return HttpResponseRedirect(self.get_success_url())
