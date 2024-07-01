from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import SeedLot, SeedlingBatch, Planting, Harvest, Location, Event


#farm/forms.py

class SeedLotForm(forms.ModelForm):
    class Meta:
        model = SeedLot
        fields = ['variety', 'name', 'quantity', 'units', 'date_received', 'origin', 'description', 'source_partner', 'source']

class SeedlingBatchForm(forms.ModelForm):
    class Meta:
        model = SeedlingBatch
        fields = ['seed_lot', 'date', 'quantity', 'units', 'location', 'status', 'parent_batch', 'source', 'variety']


class PlantingForm(forms.ModelForm):
    source_type = forms.ChoiceField(choices=[('seedlot', 'Seed Lot'), ('seedlingbatch', 'Seedling Batch'), ('planting', 'Planting')])
    source_id = forms.UUIDField()

    class Meta:
        model = Planting
        fields = ['variety', 'date', 'location', 'status', 'source_type', 'source_id']

    def __init__(self, *args, **kwargs):
        self.partner = kwargs.pop('partner', None)
        super().__init__(*args, **kwargs)
        if self.partner:
            self.fields['variety'].queryset = self.fields['variety'].queryset.filter(partner=self.partner)


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ['plants', 'date', 'quantity', 'units', 'description', 'source_partner']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description', 'parent']


class EventForm(forms.ModelForm):
    RELATED_ITEM_CHOICES = [
        ('planting', 'Planting'),
        ('seedlot', 'SeedLot'),
        ('seedlingbatch', 'SeedlingBatch'),
        ('harvest', 'Harvest'),
    ]
    related_item_type = forms.ChoiceField(choices=RELATED_ITEM_CHOICES)
    related_item_id = forms.UUIDField()

    class Meta:
        model = Event
        fields = ['type', 'date', 'description']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        related_item_type = cleaned_data.get('related_item_type')
        related_item_id = cleaned_data.get('related_item_id')

        if related_item_type and related_item_id:
            model_class = {
                'planting': Planting,
                'seedlot': SeedLot,
                'seedlingbatch': SeedlingBatch,
                'harvest': Harvest
            }.get(related_item_type)

            if model_class:
                try:
                    related_item = model_class.objects.get(id=related_item_id)
                    if self.request and self.request.user.customer != related_item.customer:
                        raise forms.ValidationError("You don't have permission to associate with this item.")
                    cleaned_data['content_type'] = ContentType.objects.get_for_model(model_class)
                    cleaned_data['object_id'] = related_item_id
                except model_class.DoesNotExist:
                    raise forms.ValidationError(f"{related_item_type.capitalize()} with id {related_item_id} does not exist.")
            else:
                raise forms.ValidationError("Invalid related item type.")

        return cleaned_data

    def save(self, commit=True):
        event = super().save(commit=False)
        event.content_type = self.cleaned_data['content_type']
        event.object_id = self.cleaned_data['object_id']
        if self.request:
            event.customer = self.request.user.customer
        if commit:
            event.save()
        return event