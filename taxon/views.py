import logging
from django.views.generic import ListView, DetailView
from .models import Taxon, Variety

logger = logging.getLogger(__name__)

class TaxonListView(ListView):
    model = Taxon
    template_name = 'taxon/taxon_list.html'
    context_object_name = 'taxons'

    def get_context_data(self, **kwargs):
        logger.debug(f"TaxonListView get_context_data called with kwargs: {kwargs}")
        context = super().get_context_data(**kwargs)
        context['taxon_type'] = self.kwargs.get('type').capitalize()
        return context

    def get_queryset(self):
        logger.debug(f"TaxonListView get_queryset called with kwargs: {self.kwargs}")
        taxon_type = self.kwargs.get('type')
        if taxon_type == 'flower':
            return Taxon.objects.filter(type__in=['annual', 'perennial'])
        else:
            return Taxon.objects.filter(type=taxon_type)

class VarietyListView(ListView):
    model = Variety
    template_name = 'taxon/variety_list.html'
    context_object_name = 'varieties'

    def get_context_data(self, **kwargs):
        logger.debug(f"VarietyListView get_context_data called with kwargs: {kwargs}")
        context = super().get_context_data(**kwargs)
        context['taxon'] = Taxon.objects.get(id=self.kwargs.get('taxon_id'))
        return context

    def get_queryset(self):
        logger.debug(f"VarietyListView get_queryset called with kwargs: {self.kwargs}")
        return Variety.objects.filter(taxon_id=self.kwargs.get('taxon_id'))

class VarietyDetailView(DetailView):
    model = Variety
    template_name = 'taxon/variety_detail.html'
    context_object_name = 'variety'

    def get_context_data(self, **kwargs):
        logger.debug(f"VarietyDetailView get_context_data called with kwargs: {kwargs}")
        context = super().get_context_data(**kwargs)
        return context


class TaxonDetailView(DetailView):
    model = Taxon
    template_name = 'taxon/taxon_detail.html'
    context_object_name = 'taxon'