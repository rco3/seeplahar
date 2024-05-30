from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Taxon, Variety

# Taxon Views
class TaxonListView(ListView):
    model = Taxon
    template_name = 'taxon/taxon_list.html'
    context_object_name = 'taxa'

class TaxonDetailView(DetailView):
    model = Taxon
    template_name = 'taxon/taxon_detail.html'
    context_object_name = 'taxon'

class TaxonCreateView(CreateView):
    model = Taxon
    template_name = 'taxon/taxon_form.html'
    fields = ['name', 'species_name', 'type', 'description']
    success_url = reverse_lazy('taxon_list')

class TaxonUpdateView(UpdateView):
    model = Taxon
    template_name = 'taxon/taxon_form.html'
    fields = ['name', 'species_name', 'type', 'description']
    success_url = reverse_lazy('taxon_list')

class TaxonDeleteView(DeleteView):
    model = Taxon
    template_name = 'taxon/taxon_confirm_delete.html'
    success_url = reverse_lazy('taxon_list')

# Variety Views
class VarietyListView(ListView):
    model = Variety
    template_name = 'taxon/variety_list.html'
    context_object_name = 'varieties'

class VarietyDetailView(DetailView):
    model = Variety
    template_name = 'taxon/variety_detail.html'
    context_object_name = 'variety'

class VarietyCreateView(CreateView):
    model = Variety
    template_name = 'taxon/variety_form.html'
    fields = ['name', 'taxon', 'description', 'origin']
    success_url = reverse_lazy('variety_list')

class VarietyUpdateView(UpdateView):
    model = Variety
    template_name = 'taxon/variety_form.html'
    fields = ['name', 'taxon', 'description', 'origin']
    success_url = reverse_lazy('variety_list')

class VarietyDeleteView(DeleteView):
    model = Variety
    template_name = 'taxon/variety_confirm_delete.html'
    success_url = reverse_lazy('variety_list')


class FruitListView(ListView):
    model = Taxon
    template_name = 'taxon/fruit_list.html'

    def get_queryset(self):
        return Taxon.objects.filter(type='fruit')


class VegetableListView(ListView):
    model = Taxon
    template_name = 'taxon/vegetable_list.html'
    context_object_name = 'vegetables'

    def get_queryset(self):
        return Taxon.objects.filter(type='vegetable')


class HerbListView(ListView):
    model = Taxon
    template_name = 'taxon/herb_list.html'

    def get_queryset(self):
        return Taxon.objects.filter(type='herb')


class FlowerListView(ListView):
    model = Variety
    template_name = 'taxon/flower_list.html'

    def get_queryset(self):
        return Taxon.objects.filter(type__in=['annual', 'perennial'])