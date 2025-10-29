from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import SeedLot, SeedlingBatch, Planting, Harvest, Location, Event


#farm/forms.py

class SeedLotForm(forms.ModelForm):
    class Meta:
        model = SeedLot
        fields = ['variety',
                  'name',
                  'quantity',
                  'units',
                  'date_received',
                  'vendor',
                  'description',
                  'source_partner',
                  'source_content_type',
                  'source_object_id']

    def __init__(self, *args, **kwargs):
        variety_id = kwargs.pop('variety_id', None)
        super().__init__(*args, **kwargs)

        if variety_id:
            # Coming from Variety detail page - hide variety field
            self.fields['variety'].widget = forms.HiddenInput()

            # Hide GenericFK fields for now (external acquisition)
            self.fields['source_content_type'].widget = forms.HiddenInput()
            self.fields['source_object_id'].widget = forms.HiddenInput()


# Update the existing SeedlingBatchForm class in farm/forms.py

class SeedlingBatchForm(forms.ModelForm):
    class Meta:
        model = SeedlingBatch
        fields = ['variety', 'date', 'quantity', 'units', 'location', 'parent_batch', 'vendor', 'source_partner',
                  'source_content_type', 'source_object_id']

    def __init__(self, *args, **kwargs):
        seedlot_id = kwargs.pop('seedlot_id', None)
        super().__init__(*args, **kwargs)

        if seedlot_id:
            # Get the specific seedlot and its variety
            try:
                seedlot = SeedLot.objects.get(pk=seedlot_id)
                variety = seedlot.variety

                # Pre-populate fields from the seedlot
                self.fields['variety'].initial = variety
                self.fields['source_content_type'].initial = ContentType.objects.get_for_model(SeedLot)
                self.fields['source_object_id'].initial = seedlot_id
                self.fields['source_partner'].initial = seedlot.source_partner
                self.fields['vendor'].initial = seedlot.vendor

                # Hide variety field since it's determined by seedlot
                self.fields['variety'].widget = forms.HiddenInput()

                # Hide the GenericFK fields - they're set automatically
                self.fields['source_content_type'].widget = forms.HiddenInput()
                self.fields['source_object_id'].widget = forms.HiddenInput()

                # Make source_partner and vendor readonly (inherited from seedlot)
                self.fields['source_partner'].widget.attrs['readonly'] = True
                self.fields['source_partner'].widget.attrs['class'] = 'readonly-field bg-gray-100'
                self.fields['vendor'].widget.attrs['readonly'] = True
                self.fields['vendor'].widget.attrs['class'] = 'readonly-field bg-gray-100'

            except SeedLot.DoesNotExist:
                pass  # Handle gracefully if seedlot not found


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


# farm/forms.py - Updated EventForm

class EventForm(forms.ModelForm):
    # Remove hard-coded choices - let the GenericFK be truly generic!
    related_item_type = forms.CharField(max_length=50, help_text="e.g., 'planting', 'seedlot', 'harvest'")
    related_item_id = forms.UUIDField()

    class Meta:
        model = Event
        fields = ['type', 'date', 'description']
        widgets = {
            'type': forms.TextInput(attrs={
                'list': 'event-types-datalist',
                'placeholder': 'Enter event type...',
                'autocomplete': 'off'
            })
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Add datalist options for autocomplete - both event types AND model types
        if self.request and self.request.user.customer:
            existing_types = Event.objects.filter(
                customer=self.request.user.customer
            ).values_list('type', flat=True).distinct().order_by('type')

            existing_model_types = Event.objects.filter(
                customer=self.request.user.customer
            ).values_list('content_type__model', flat=True).distinct().order_by('content_type__model')

            self.existing_event_types = list(existing_types)
            self.existing_model_types = list(existing_model_types)

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
                    raise forms.ValidationError(
                        f"{related_item_type.capitalize()} with id {related_item_id} does not exist.")
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