from django.views.generic import DetailView, CreateView
from .models import Plant, SeedLot, SeedlingBatch, Harvest, Event

class PlantDetailView(DetailView):
    model = Plant
    template_name = 'farm/plant_detail.html'
    context_object_name = 'plant'

class SeedLotDetailView(DetailView):
    model = SeedLot
    template_name = 'farm/seedlot_detail.html'
    context_object_name = 'seedlot'

class SeedlingBatchDetailView(DetailView):
    model = SeedlingBatch
    template_name = 'farm/seedlingbatch_detail.html'
    context_object_name = 'seedlingbatch'

class HarvestDetailView(DetailView):
    model = Harvest
    template_name = 'farm/harvest_detail.html'
    context_object_name = 'harvest'

class EventAddView(CreateView):
    model = Event
    fields = ['event_type', 'description', 'date']
    template_name = 'farm/event_form.html'

    def form_valid(self, form):
        form.instance.object_id = self.kwargs['pk']
        return super().form_valid(form)
