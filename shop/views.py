from django.views.generic import ListView, DetailView
from .models import SeedPackage, ProducePackage, PlantPackage
from media.models import Photo

class SeedPackageDetailView(DetailView):
    model = SeedPackage
    template_name = 'shop/seedpackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='seedpackage', object_id=self.object.id)
        return context

class ProducePackageDetailView(DetailView):
    model = ProducePackage
    template_name = 'shop/producepackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='producepackage', object_id=self.object.id)
        return context

class PlantPackageDetailView(DetailView):
    model = PlantPackage
    template_name = 'shop/plantpackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = Photo.objects.filter(content_type__model='plantpackage', object_id=self.object.id)
        return context
