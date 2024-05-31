from taxon.models import Photo
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from taxon.models import Variety
from farm.models import Event, Plant, SeedLot, SeedlingBatch, Harvest

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = [
            {
                'name': 'Fruits',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'fruit'}),
                'image': '/static/images/fruit.jpg'
            },
            {
                'name': 'Vegetables',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'vegetable'}),
                'image': '/static/images/vegetable.jpg'
            },
            {
                'name': 'Herbs',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'herb'}),
                'image': '/static/images/herb.jpg'
            },
            {
                'name': 'Flowers',
                'url': reverse_lazy('taxon:taxon-list', kwargs={'type': 'flower'}),
                'image': '/static/images/flower.jpg'
            },
        ]
        return context


class GenericDetailView(View):

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get('pk')

        # Try to get a Variety
        try:
            variety = Variety.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('taxon:variety-detail', kwargs={'pk': uuid}))
        except Variety.DoesNotExist:
            pass

        # Try to get other farm objects and redirect accordingly
        try:
            event = Event.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('farm:event-add', kwargs={'pk': uuid}))
        except Event.DoesNotExist:
            pass

        try:
            plant = Plant.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('farm:plant-detail', kwargs={'pk': uuid}))
        except Plant.DoesNotExist:
            pass

        try:
            seed_lot = SeedLot.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('farm:seedlot-detail', kwargs={'pk': uuid}))
        except SeedLot.DoesNotExist:
            pass

        try:
            seedling_batch = SeedlingBatch.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('farm:seedlingbatch-detail', kwargs={'pk': uuid}))
        except SeedlingBatch.DoesNotExist:
            pass

        try:
            harvest = Harvest.objects.get(pk=uuid)
            return HttpResponseRedirect(reverse('farm:harvest-detail', kwargs={'pk': uuid}))
        except Harvest.DoesNotExist:
            pass

        raise Http404("Object does not exist")

