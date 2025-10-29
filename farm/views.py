from django.contrib.contenttypes.models import ContentType
from django.views import View
from django.http import HttpResponse
import qrcode
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from seeplahar.views.base import BaseCreateView
from seeplahar.views.generic import GenericCreateView, GenericUpdateView
from django.urls import reverse_lazy
from .models import Planting, SeedLot, SeedlingBatch, Location, Event
from .forms import PlantingForm, SeedLotForm, SeedlingBatchForm, LocationForm, EventForm


# farm/views.py

class FarmCreateView(BaseCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_form'] = LocationForm()
        return context

    def form_valid(self, form):
        location_form = LocationForm(self.request.POST)
        if location_form.is_valid():
            location = location_form.save(commit=False)
            location.customer = self.request.user.customer
            location.save()
            form.instance.location = location
        return super().form_valid(form)


class PlantingCreateView(FarmCreateView, GenericCreateView):
    model = Planting
    form_class = PlantingForm
    success_url = reverse_lazy('farm:planting_list')
    template_name = 'farm/planting_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['source'].choices = self.get_source_choices()
        return form

    def get_source_choices(self):
        choices = [
            ('partner', 'Acquire from a Partner'),
            ('planting', 'Clone from another Planting'),
            ('seedlingbatch', 'Plant from a SeedlingBatch'),
            ('seedlot', 'Plant from a SeedLot'),
        ]
        return choices


class SeedLotCreateView(FarmCreateView, GenericCreateView):
    model = SeedLot
    form_class = SeedLotForm
    success_url = reverse_lazy('farm:seedlot_list')
    template_name = 'farm/seedlot_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        variety_id = self.request.GET.get('variety')
        if variety_id:
            kwargs['variety_id'] = variety_id
            # Pre-populate the instance if creating from variety
            if not kwargs.get('instance'):
                from taxon.models import Variety
                variety = get_object_or_404(Variety, pk=variety_id, customer=self.request.user.customer)
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['variety'] = variety
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variety_id = self.request.GET.get('variety')
        if variety_id:
            from taxon.models import Variety
            context['variety'] = get_object_or_404(Variety, pk=variety_id, customer=self.request.user.customer)
        return context


class SeedlingBatchCreateView(FarmCreateView, GenericCreateView):
    model = SeedlingBatch
    form_class = SeedlingBatchForm
    success_url = reverse_lazy('farm:seedlingbatch_list')
    template_name = 'farm/seedlingbatch_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        seedlot_id = self.request.GET.get('seedlot')
        if seedlot_id:
            kwargs['seedlot_id'] = seedlot_id
            # Pre-populate the instance if creating from seedlot
            if not kwargs.get('instance'):
                seedlot = get_object_or_404(SeedLot, pk=seedlot_id, customer=self.request.user.customer)
                kwargs['initial'] = kwargs.get('initial', {})
                kwargs['initial']['seed_lot'] = seedlot
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seedlot_id = self.request.GET.get('seedlot')
        if seedlot_id:
            context['seedlot'] = get_object_or_404(SeedLot, pk=seedlot_id, customer=self.request.user.customer)
        return context


class EventCreateView(GenericCreateView):
    model = Event
    form_class = EventForm
    template_name = 'farm/event_form.html'
    success_url = reverse_lazy('farm:event_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)


class EventUpdateView(GenericUpdateView):
    model = Event
    form_class = EventForm
    template_name = 'farm/event_form.html'
    success_url = reverse_lazy('farm:event_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

#
# class GenerateQRCodeView(View):
#     def get(self, request, pk):
#         qr_url = f"{request.scheme}://{request.get_host()}/{pk}/"
#         qr = qrcode.make(qr_url)
#         response = HttpResponse(content_type="image/png")
#         qr.save(response, "PNG")
#         return response


class IntakeView(TemplateView):
    template_name = "farm/intake.html"