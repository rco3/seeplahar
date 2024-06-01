from django.views.generic import ListView, DetailView
from .models import SeedLot, Plant, Harvest, SeedlingBatch
from django.urls import reverse_lazy
from media.models import Photo
from django.views.generic.edit import CreateView
from .models import Event

class SeedLotDetailView(DetailView):
    model = SeedLot
    template_name = 'farm/seedlot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='seedlot', object_id=self.object.id)
        return context

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'farm/plant_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='plant', object_id=self.object.id)
        return context

class HarvestDetailView(DetailView):
    model = Harvest
    template_name = 'farm/harvest_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='harvest', object_id=self.object.id)
        return context

class SeedlingBatchDetailView(DetailView):
    model = SeedlingBatch
    template_name = 'farm/seedlingbatch_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='seedlingbatch', object_id=self.object.id)
        return context


class EventAddView(CreateView):
    model = Event
    template_name = 'farm/event_form.html'
    fields = ['type', 'date', 'description', 'related_item']
    success_url = reverse_lazy('farm:event-list')