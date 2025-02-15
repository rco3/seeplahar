# seeplahar/views/base.py
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from users.customer_context import get_current_customer
import logging

class CustomerAwareView(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        # print(f"CustomerAwareView dispatch: User: {request.user}, Customer: {get_current_customer()}")
        # if not get_current_customer():
        #     print("Warning: No customer set in CustomerAwareView dispatch")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        customer = get_current_customer()
        # print(f"CustomerAwareView get_queryset: Customer: {customer}")
        if customer:
            return queryset.filter(customer=customer)
        # print("Warning: No customer set, returning empty queryset")
        return queryset.none()


class BaseListView(CustomerAwareView, ListView):
    template_name = 'base_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        return context


class BaseDetailView(CustomerAwareView, DetailView):
    template_name = 'base_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        return context


class BaseCreateView(CustomerAwareView, CreateView):
    template_name = 'base_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        context['action'] = 'Create'
        return context

    def get_success_url(self):
        return reverse_lazy(f'{self.model._meta.app_label}:{self.model._meta.model_name}_detail', kwargs={'pk': self.object.pk})


class BaseUpdateView(CustomerAwareView, UpdateView):
    template_name = 'base_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        context['action'] = 'Update'
        return context

    def get_success_url(self):
        return reverse_lazy(f'{self.model._meta.app_label}:{self.model._meta.model_name}_detail', kwargs={'pk': self.object.pk})


class BaseDeleteView(CustomerAwareView, DeleteView):
    template_name = 'base_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view'] = self
        return context

    def get_success_url(self):
        return reverse_lazy(f'{self.model._meta.app_label}:{self.model._meta.model_name}_list')