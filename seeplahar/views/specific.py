from taxon.models import Photo
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth import login as auth_login
from farm.models import Event, Planting, SeedLot, SeedlingBatch, Harvest
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from users.customer_context import get_current_customer
from taxon.models import Taxon, Variety
from users.models import Partner


class CustomLoginView(View):
    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('/')
        return render(request, 'registration/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('/')

class DashboardView(PermissionRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    permission_required = ('farm.add_seedlot', 'taxon.add_variety')
    raise_exception = True  # Raise a 403 Forbidden if permission is denied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_perm'] = self.request.user.has_perm
        return context

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = [
            {
                'name': 'Fruits',
                'url': reverse_lazy('taxon:taxon_type_list', kwargs={'type': 'fruit'}),
                'image': '/static/images/fruit.jpg'
            },
            {
                'name': 'Vegetables',
                'url': reverse_lazy('taxon:taxon_type_list', kwargs={'type': 'vegetable'}),
                'image': '/static/images/vegetable.jpg'
            },
            {
                'name': 'Herbs',
                'url': reverse_lazy('taxon:taxon_type_list', kwargs={'type': 'herb'}),
                'image': '/static/images/herb.jpg'
            },
            {
                'name': 'Flowers',
                'url': reverse_lazy('taxon:taxon_type_list', kwargs={'type': 'flower'}),
                'image': '/static/images/flower.jpg'
            },
        ]
        return context


# Add this to seeplahar/views/specific.py


class UniversalDetailView(View):
    """
    Universal UUID lookup view that searches across all models
    to find which one contains the given UUID, then redirects
    to the appropriate detail view.
    """

    def get(self, request, pk):
        customer = get_current_customer()

        # (model_class, app_label, model_name matching _meta.model_name)
        models_to_check = [
            # Farm operations (most commonly scanned)
            (SeedLot, 'farm', 'seedlot'),
            (Planting, 'farm', 'planting'),
            (Harvest, 'farm', 'harvest'),
            (SeedlingBatch, 'farm', 'seedlingbatch'),

            # Taxonomy (less frequently scanned directly)
            (Variety, 'taxon', 'variety'),
            (Taxon, 'taxon', 'taxon'),

            # Admin objects (rarely scanned)
            (Partner, 'users', 'partner'),
        ]

        for model_class, app_label, model_name in models_to_check:
            try:
                model_class.objects.get(pk=pk, customer=customer)
                return redirect(f'{app_label}:{model_name}_detail', pk=pk)
            except model_class.DoesNotExist:
                continue

        raise Http404(f"No object found with ID {pk}")