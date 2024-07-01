from taxon.models import Photo
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth import login as auth_login
from taxon.models import Variety
from farm.models import Event, Planting, SeedLot, SeedlingBatch, Harvest
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import PermissionRequiredMixin


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
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'fruit'}),
                'image': '/static/images/fruit.jpg'
            },
            {
                'name': 'Vegetables',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'vegetable'}),
                'image': '/static/images/vegetable.jpg'
            },
            {
                'name': 'Herbs',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'herb'}),
                'image': '/static/images/herb.jpg'
            },
            {
                'name': 'Flowers',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'flower'}),
                'image': '/static/images/flower.jpg'
            },
        ]
        return context
