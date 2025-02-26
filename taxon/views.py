from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages

from farm.models import SeedLot
from seeplahar.views import GenericDeleteView, GenericCreateView, GenericListView, GenericDetailView
from .models import Taxon, Variety, Characteristic, CharacteristicValue
from .forms import VarietyForm, TaxonForm, CharacteristicForm, CharacteristicFormSet, CharacteristicValueForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from django.http import JsonResponse
from autocomplete import HTMXAutoComplete
from django.forms import inlineformset_factory

def add_characteristic_form(request):
    if request.method == 'POST':
        form = CharacteristicForm(request.POST)
        if form.is_valid():
            characteristic = form.save(commit=False)
            characteristic.customer = request.user.customer
            characteristic.save()
            formset = CharacteristicFormSet(request.POST, instance=characteristic)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Characteristic added successfully.')
                return redirect('taxon:taxon_list')
            else:
                messages.error(request, 'Error in characteristic values.')
        else:
            messages.error(request, 'Error in characteristic form.')
    else:
        form = CharacteristicForm()
        formset = CharacteristicFormSet()

    return render(request, 'taxon/characteristic_form.html', {
        'form': form,
        'formset': formset
    })


class CharacteristicNameAutoComplete(HTMXAutoComplete):
    name = 'characteristic_name'
    route_name = 'characteristic_name_autocomplete'

    class Meta:
        model = Characteristic
        field = 'name'

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        if term:
            suggestions = Characteristic.objects.filter(name__icontains=term, customer=request.user.customer).values(
                'name').distinct()
            return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})
        suggestions = Characteristic.objects.filter(customer=request.user.customer).values('name').distinct()
        return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})


class CharacteristicValueAutoComplete(HTMXAutoComplete):
    name = 'characteristic_value'
    route_name = 'characteristic_value_autocomplete'

    class Meta:
        model = CharacteristicValue
        field = 'value'

    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        characteristic_name = request.GET.get('characteristic_name', '')
        if term and characteristic_name:
            suggestions = CharacteristicValue.objects.filter(
                value__icontains=term,
                characteristic__name=characteristic_name,
                characteristic__customer=request.user.customer
            ).values('value').distinct()
            return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': list(suggestions)})
        return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': []})


def test_autocomplete(request):
    return render(request, 'taxon/test_autocomplete.html')


class TaxonListView(GenericListView):
    model = Taxon
    template_name = 'taxon/taxon_list.html'
    context_object_name = 'taxons'

    def get_queryset(self):
        queryset = super().get_queryset()
        taxon_type = self.kwargs.get('type')
        if taxon_type:
            if taxon_type == 'flower':
                queryset = queryset.filter(type__in=['annual', 'perennial'])
            else:
                queryset = queryset.filter(type=taxon_type)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxon_type'] = self.kwargs.get('type', 'All').capitalize()
        return context


class VarietyListView(GenericListView):
    model = Variety
    template_name = 'taxon/variety_list.html'
    context_object_name = 'varieties'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxon'] = Taxon.objects.get(id=self.kwargs.get('taxon_id'))
        return context

    def get_queryset(self):
        return super().get_queryset().filter(taxon_id=self.kwargs.get('taxon_id'))


class VarietyDeleteView(GenericDeleteView):
    model = Variety

    def get_success_url(self):
        return reverse('taxon:variety_list', kwargs={
            'type': self.object.taxon.type,
            'taxon_id': str(self.object.taxon.id)
        })

class VarietyDetailView(GenericDetailView):
    model = Variety
    template_name = 'taxon/variety_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seed_lots'] = SeedLot.objects.filter(variety=self.object)
        # Expose app_label and model_name for use in the template.
        context['app_label'] = self.object._meta.app_label
        context['model_name'] = self.object._meta.model_name
        return context


class VarietyCreateView(GenericCreateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'taxon/variety_form.html'
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        CharacteristicValueFormSet = inlineformset_factory(
            Variety,
            CharacteristicValue,
            form=CharacteristicValueForm,
            extra=1,
            can_delete=True
        )
        if self.request.POST:
            data['characteristic_value_formset'] = CharacteristicValueFormSet(self.request.POST, instance=self.object)
        else:
            data['characteristic_value_formset'] = CharacteristicValueFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        characteristic_value_formset = context['characteristic_value_formset']
        print(f"Main form valid: {form.is_valid()}")
        print(f"Main form errors: {form.errors}")
        print(f"Formset valid: {characteristic_value_formset.is_valid()}")
        print(f"Formset errors: {characteristic_value_formset.errors}")
        print(f"Formset non-form errors: {characteristic_value_formset.non_form_errors()}")
        print(f"Formset management form data: {characteristic_value_formset.management_form.cleaned_data}")

        if form.is_valid() and characteristic_value_formset.is_valid():
            self.object = form.save()
            characteristic_value_formset.instance = self.object
            characteristic_value_formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


    def form_invalid(self, form):
        print(f"Form invalid. Errors: {form.errors}")
        return super().form_invalid(form)


class TaxonDeleteView(GenericDeleteView):
    model = Taxon

    def get_success_url(self):
        return reverse('taxon:taxon_type_list', kwargs={'type': self.object.type})