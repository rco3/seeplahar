from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages

from farm.models import SeedLot
from seeplahar.views import GenericDeleteView, GenericCreateView, GenericListView, GenericDetailView, GenericUpdateView
from .models import Taxon, Variety, Characteristic, CharacteristicValue
from .forms import VarietyForm, TaxonForm, CharacteristicForm, CharacteristicFormSet, CharacteristicValueForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.forms import modelformset_factory
from django.http import JsonResponse
from autocomplete import HTMXAutoComplete
from django.forms import inlineformset_factory
from users.customer_context import get_current_customer



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
        char_name = request.GET.get('char-name', '')  # Note: 'char-name' not 'characteristic_name'
        print(f"DEBUG: term='{term}', char_name='{char_name}'")  # Add this line
        customer = get_current_customer()

        if char_name:
            try:
                characteristic = Characteristic.objects.get(name=char_name, customer=customer)
                values = CharacteristicValue.objects.filter(characteristic=characteristic)
                if term:
                    values = values.filter(value__icontains=term)
                # Get unique values only
                unique_values = values.values_list('value', flat=True).distinct()
                suggestions = [{'name': char_name, 'value': value} for value in unique_values]
            except Characteristic.DoesNotExist:
                suggestions = []
        else:
            suggestions = []

        return render(request, 'taxon/autocomplete_suggestions.html', {'suggestions': suggestions})

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
        return queryset.prefetch_related('photos', 'varieties__photos')

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
        return super().get_queryset().filter(
            taxon_id=self.kwargs.get('taxon_id')
        ).prefetch_related('photos')


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
        context['app_label'] = self.object._meta.app_label
        context['model_name'] = self.object._meta.model_name
        return context


class VarietyCreateView(GenericCreateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'taxon/variety_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # Save the variety first
        form.instance.customer = get_current_customer()
        self.object = form.save()

        # Process characteristics from JavaScript-generated fields
        i = 0
        while f'characteristic_{i}_name' in self.request.POST:
            char_name = self.request.POST[f'characteristic_{i}_name']
            char_value = self.request.POST[f'characteristic_{i}_value']

            if char_name and char_value:
                # Get or create the characteristic
                characteristic, _ = Characteristic.objects.get_or_create(
                    name=char_name,
                    customer=get_current_customer()
                )

                # Create the characteristic value
                CharacteristicValue.objects.create(
                    characteristic=characteristic,
                    value=char_value,
                    variety=self.object
                )
            i += 1

        return super().form_valid(form)


class VarietyUpdateView(GenericUpdateView):
    model = Variety
    form_class = VarietyForm
    template_name = 'taxon/variety_form.html'  # Can use the same template
    success_url = reverse_lazy('dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add existing characteristics to context for display
        context['existing_characteristics'] = CharacteristicValue.objects.filter(variety=self.object)
        return context

    def form_valid(self, form):
        # Save the variety first
        self.object = form.save()

        # Clear existing characteristics for this variety
        CharacteristicValue.objects.filter(variety=self.object).delete()

        # Process new characteristics from JavaScript-generated fields
        i = 0
        while f'characteristic_{i}_name' in self.request.POST:
            char_name = self.request.POST[f'characteristic_{i}_name']
            char_value = self.request.POST[f'characteristic_{i}_value']

            if char_name and char_value:
                characteristic, _ = Characteristic.objects.get_or_create(
                    name=char_name,
                    customer=get_current_customer()
                )

                CharacteristicValue.objects.create(
                    characteristic=characteristic,
                    value=char_value,
                    variety=self.object
                )
            i += 1

        return super().form_valid(form)


class TaxonDeleteView(GenericDeleteView):
    model = Taxon

    def get_success_url(self):
        return reverse('taxon:taxon_type_list', kwargs={'type': self.object.type})