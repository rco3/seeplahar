from django.urls import reverse_lazy
from django.views.generic import DetailView
from .models import SeedPackage, ProducePackage, PlantPackage
from django.contrib.contenttypes.models import ContentType
from media.models import Photo
from seeplahar.views.generic import GenericDetailView, GenericCreateView


class PhotoMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type = ContentType.objects.get_for_model(self.model)
        context['photos'] = Photo.objects.filter(content_type=content_type, object_id=self.object.id)
        return context


class SeedPackageDetailView(PhotoMixin, GenericDetailView):
    model = SeedPackage
    template_name = 'base_detail.html'  # Use a generic template


class ProducePackageDetailView(PhotoMixin, GenericDetailView):
    model = ProducePackage
    template_name = 'base_detail.html'  # Use a generic template


class PlantPackageDetailView(PhotoMixin, GenericDetailView):
    model = PlantPackage
    template_name = 'base_detail.html'  # Use a generic template


class SeedPackageCreateView(GenericCreateView):
    model = SeedPackage
    fields = ['seed_lot', 'quantity', 'quantity_units', 'date_packaged', 'description', 'photos']
    success_url = reverse_lazy('shop:seedpackage_list')

class ProducePackageCreateView(GenericCreateView):
    model = ProducePackage
    fields = ['harvest', 'quantity', 'quantity_units', 'date_packaged', 'description', 'photos']
    success_url = reverse_lazy('shop:producepackage_list')

class PlantPackageCreateView(GenericCreateView):
    model = PlantPackage
    fields = ['plants', 'date_packaged', 'quantity', 'description', 'seedling_batch', 'photos']
    success_url = reverse_lazy('shop:plantpackage_list')