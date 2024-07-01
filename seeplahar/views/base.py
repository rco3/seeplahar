# seeplahar/views/base.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from users.middleware import get_current_customer

class CustomerAwareView(LoginRequiredMixin):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        else:
            return super().get_queryset().filter(customer=get_current_customer())

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