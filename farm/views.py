from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import SeedLot, Plant, Harvest, SeedlingBatch, Event
from django.urls import reverse_lazy
from media.models import Photo
from django.contrib.contenttypes.models import ContentType


class SeedLotListView(ListView):
    model = SeedLot
    template_name = 'farm/seedlot_list.html'
    context_object_name = 'seedlots'


class SeedLotDetailView(DetailView):
    model = SeedLot
    template_name = 'farm/seedlot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seedlot_content_type = ContentType.objects.get_for_model(SeedLot)
        context['photos'] = Photo.objects.filter(content_type=seedlot_content_type, object_id=self.object.id)
        return context


class PlantListView(ListView):
    model = Plant
    template_name = 'farm/plant_list.html'
    context_object_name = 'plants'

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'farm/plant_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plant_content_type = ContentType.objects.get_for_model(Plant)
        context['photos'] = Photo.objects.filter(content_type=plant_content_type, object_id=self.object.id)
        return context


class HarvestListView(ListView):
    model = Harvest
    template_name = 'farm/harvest_list.html'
    context_object_name = 'harvests'


class HarvestDetailView(DetailView):
    model = Harvest
    template_name = 'farm/harvest_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        harvest_content_type = ContentType.objects.get_for_model(Harvest)
        context['photos'] = Photo.objects.filter(content_type=harvest_content_type, object_id=self.object.id)
        return context


class SeedlingBatchListView(ListView):
    model = SeedlingBatch
    template_name = 'farm/seedlingbatch_list.html'
    context_object_name = 'seedling_batches'


class SeedlingBatchDetailView(DetailView):
    model = SeedlingBatch
    template_name = 'farm/seedlingbatch_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seedlingbatch_content_type = ContentType.objects.get_for_model(SeedlingBatch)
        context['photos'] = Photo.objects.filter(content_type=seedlingbatch_content_type, object_id=self.object.id)
        return context


class EventListView(ListView):
    model = Event
    template_name = 'farm/event_list.html'
    context_object_name = 'events'


class EventDetailView(DetailView):
    model = Event
    template_name = 'farm/event_detail.html'


class EventAddView(CreateView):
    model = Event
    template_name = 'farm/event_form.html'
    fields = ['type', 'date', 'description', 'related_item']
    success_url = reverse_lazy('farm:event_list')

    def form_invalid(self, form):
        print(form.errors)  # Print form errors for debugging
        return super().form_invalid(form)