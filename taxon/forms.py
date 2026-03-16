from django import forms
from .models import Variety, Taxon, Characteristic, CharacteristicValue
from django.forms import inlineformset_factory
from autocomplete import HTMXAutoComplete, widgets

# taxon/forms.py

class VarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = ['name', 'taxon', 'description']

class CharacteristicForm(forms.ModelForm):
    class Meta:
        model = Characteristic
        fields = ['name']
        widgets = {
            'name': widgets.Autocomplete(
                name='characteristic_name',
                options=dict(model=Characteristic, field='name')
            ),
        }

class CharacteristicValueForm(forms.ModelForm):
    class Meta:
        model = CharacteristicValue
        fields = ['characteristic', 'value']
        widgets = {
            'characteristic': forms.HiddenInput(),
            'value': widgets.Autocomplete(
                name='characteristic_value',
                options=dict(model=CharacteristicValue, field='value')
            ),
        }

CharacteristicFormSet = forms.inlineformset_factory(
    Characteristic,
    CharacteristicValue,
    form=CharacteristicValueForm,
    extra=1,
    can_delete=True
)


class TaxonForm(forms.ModelForm):
    class Meta:
        model = Taxon
        fields = ['name', 'species_name', 'type', 'description']

