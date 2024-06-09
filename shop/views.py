from django.views.generic import ListView, DetailView
from .models import SeedPackage, ProducePackage, PlantPackage
from media.models import Photo
from django.contrib.contenttypes.models import ContentType


class SeedPackageDetailView(DetailView):
    model = SeedPackage
    template_name = 'shop/seedpackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seedpackage_content_type = ContentType.objects.get_for_model(SeedPackage)
        context['photos'] = Photo.objects.filter(content_type=seedpackage_content_type, object_id=self.object.id)
        return context

class ProducePackageDetailView(DetailView):
    model = ProducePackage
    template_name = 'shop/producepackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        producepackage_content_type = ContentType.objects.get_for_model(ProducePackage)
        context['photos'] = Photo.objects.filter(content_type=producepackage_content_type, object_id=self.object.id)
        return context

class PlantPackageDetailView(DetailView):
    model = PlantPackage
    template_name = 'shop/plantpackage_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plantpackage_content_type = ContentType.objects.get_for_model(PlantPackage)
        context['photos'] = Photo.objects.filter(content_type=plantpackage_content_type, object_id=self.object.id)
        return context
