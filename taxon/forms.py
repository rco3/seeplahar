from django import forms
from .models import Variety, Taxon, Synonym, Characteristic
from django.forms import inlineformset_factory
from autocomplete import HTMXAutoComplete, widgets

# taxon/forms.py

class VarietyForm(forms.ModelForm):
    class Meta:
        model = Variety
        fields = ['name', 'taxon', 'description', 'photos']

# class CharacteristicForm(forms.ModelForm):
#     class Meta:
#         model = Characteristic
#         fields = ['name', 'value']


class CharacteristicForm(forms.ModelForm):
    class Meta:
        model = Characteristic
        fields = ['name', 'value']
        widgets = {
            'name': widgets.Autocomplete(
                name='characteristic_name',
                options=dict(model=Characteristic, field='name')
            ),
            'value': widgets.Autocomplete(
                name='characteristic_value',
                options=dict(model=Characteristic, field='value')
            )
        }


class TaxonForm(forms.ModelForm):
    class Meta:
        model = Taxon
        fields = ['name', 'species_name', 'type', 'description']

class SynonymForm(forms.ModelForm):
    class Meta:
        model = Synonym
        fields = ['name', 'taxon']
