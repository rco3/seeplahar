import logging
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Taxon, Variety, Synonym, Characteristic
from .forms import VarietyForm, TaxonForm, SynonymForm, CharacteristicForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from django.http import JsonResponse
from autocomplete import HTMXAutoComplete

# taxon/views.py
def add_characteristic_form(request):
    CharacteristicFormSet = modelformset_factory(Characteristic, form=CharacteristicForm, extra=1)
    formset = CharacteristicFormSet(queryset=Characteristic.objects.none())
    return render(request, 'taxon/characteristic_form.html', {'formset': formset})


logger = logging.getLogger(__name__)


# def characteristic_name_autocomplete(request):
#     term = request.GET.get('term', '')
#     print(f"Search term received: {term}")  # Debugging line
#
#     suggestions = Characteristic.objects.filter(name__istartswith=term).values_list('name', flat=True).distinct()
#     return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': suggestions})
#
#
# def characteristic_value_autocomplete(request):
#     term = request.GET.get('term', '')
#     suggestions = Characteristic.objects.filter(value__istartswith=term).values_list('value', flat=True).distinct()
#     return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': suggestions})

# def characteristic_name_autocomplete(request):
#     term = request.GET.get('term', '')
#     print(f"Search term received (name): {term}")  # Debugging line
#     if term:
#         suggestions = Characteristic.objects.filter(name__istartswith=term).values_list('name', flat=True).distinct()
#     else:
#         suggestions = Characteristic.objects.values_list('name', flat=True).distinct()
#     return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': suggestions})
#
#
# def characteristic_value_autocomplete(request):
#     term = request.GET.get('term', '')
#     characteristic_name = request.GET.get('characteristic_name', '')
#     print(f"Search term received (value): {term}, characteristic_name: {characteristic_name}")  # Debugging line
#     if characteristic_name:
#         suggestions = Characteristic.objects.filter(name=characteristic_name, value__istartswith=term).values_list('value', flat=True).distinct()
#     else:
#         suggestions = []
#     return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': suggestions})

def characteristic_autocomplete(request):
    term = request.GET.get('term', '')
    print(f"Autocomplete search term: {term}")  # Debug print
    if term:
        suggestions = Characteristic.objects.filter(
            name__icontains=term
        ).values('name', 'value').distinct()
        print(f"Autocomplete suggestions: {suggestions}")  # Debug print
        return JsonResponse({'suggestions': list(suggestions)})
    suggestions = Characteristic.objects.all().values('name', 'value').distinct()
    return JsonResponse({'suggestions': list(suggestions)})


class CharacteristicNameAutoComplete(HTMXAutoComplete):
    name = 'characteristic_name'
    route_name = 'characteristic_name_autocomplete'

    class Meta:
        model = Characteristic
        field = 'name'

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        print(f"CharacteristicNameAutoComplete search term: {term}")  # Debug print
        if term:
            suggestions = Characteristic.objects.filter(name__icontains=term).values('name', 'value').distinct()
            print(f"CharacteristicNameAutoComplete suggestions: {suggestions}")  # Debug print
            return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})
        suggestions = Characteristic.objects.all().values('name', 'value').distinct()
        return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})

class CharacteristicValueAutoComplete(HTMXAutoComplete):
    name = 'characteristic_value'
    route_name = 'characteristic_value_autocomplete'

    class Meta:
        model = Characteristic
        field = 'value'

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        characteristic_name = request.GET.get('characteristic_name', '')
        print(f"CharacteristicValueAutoComplete search term: {term}, characteristic_name: {characteristic_name}")  # Debug print
        if term and characteristic_name:
            suggestions = Characteristic.objects.filter(value__icontains=term, name=characteristic_name).values('value', 'name').distinct()
            print(f"CharacteristicValueAutoComplete suggestions: {suggestions}")  # Debug print
            return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})
        return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': []})

def test_autocomplete(request):
    return render(request, 'taxon/test_autocomplete.html')


class VarietyCreateView(CreateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'taxon/variety_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        CharacteristicFormSet = modelformset_factory(Characteristic, form=CharacteristicForm, extra=1)
        if self.request.POST:
            data['characteristic_formset'] = CharacteristicFormSet(self.request.POST)
        else:
            data['characteristic_formset'] = CharacteristicFormSet(queryset=Characteristic.objects.none())
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        characteristic_formset = context['characteristic_formset']
        if form.is_valid() and characteristic_formset.is_valid():
            self.object = form.save()
            characteristics = characteristic_formset.save(commit=False)
            for characteristic in characteristics:
                characteristic.save()
                self.object.characteristics.add(characteristic)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        characteristic_formset = context['characteristic_formset']
        return self.render_to_response(self.get_context_data(form=form, characteristic_formset=characteristic_formset))


class TaxonCreateView(CreateView):
    model = Taxon
    form_class = TaxonForm
    template_name = 'taxon/taxon_form.html'
    success_url = reverse_lazy('dashboard')


class SynonymCreateView(CreateView):
    model = Synonym
    form_class = SynonymForm
    template_name = 'taxon/synonym_form.html'
    success_url = reverse_lazy('dashboard')


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



class TaxonDetailView(DetailView):
    model = Taxon
    template_name = 'taxon/taxon_detail.html'
    context_object_name = 'taxon'



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
        context = super().get_context_data(**kwargs)
        context['seed_lots'] = self.object.seed_lots.all()
        context['photos'] = self.object.photos.all()
        return context



def TaxonTestListView(request):
    taxons = Taxon.objects.all()
    return render(request, 'taxon/taxon_test_list.html', {'taxons': taxons})


