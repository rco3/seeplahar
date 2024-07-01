from django.apps import apps
from django.http import Http404
from django.urls import reverse

from .base import BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView


class GenericModelView:
    def dispatch(self, request, *args, **kwargs):
        self.app_name = self.model._meta.app_label
        self.model_name = self.model._meta.model_name
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_fields'] = [
            {'name': field.name, 'verbose_name': field.verbose_name}
            for field in self.model._meta.fields
        ]
        context['model_name'] = self.model._meta.verbose_name
        context['model_name_plural'] = self.model._meta.verbose_name_plural
        context['app_label'] = self.app_name

        # Generate URL names
        base_name = f"{self.app_name}:{self.model_name}"
        context['list_url_name'] = f"{base_name}_list"
        context['detail_url_name'] = f"{base_name}_detail"
        context['create_url_name'] = f"{base_name}_create"
        context['update_url_name'] = f"{base_name}_update"
        context['delete_url_name'] = f"{base_name}_delete"

        return context


class GenericListView(GenericModelView, BaseListView):
    template_name = 'base_list.html'


class GenericDetailView(GenericModelView, BaseDetailView):
    template_name = 'base_detail.html'


class GenericCreateView(GenericModelView, BaseCreateView):
    template_name = 'base_form.html'


class GenericUpdateView(GenericModelView, BaseUpdateView):
    template_name = 'base_form.html'


class GenericDeleteView(GenericModelView, BaseDeleteView):
    template_name = 'base_confirm_delete.html'

    def get_success_url(self):
        return reverse(f'{self.model._meta.app_label}:{self.model._meta.model_name}_list')