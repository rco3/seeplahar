from taxon.models import Photo
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.views import View
from taxon.models import Taxon, Variety

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
    def get(self, request, pk):
        # Attempt to get the object by UUID from different models
        try:
            obj = get_object_or_404(Variety, pk=pk)
            template_name = 'taxon/variety_detail.html'
            context = {'variety': obj, 'type': 'Variety'}
        except:
            try:
                obj = get_object_or_404(Taxon, pk=pk)
                template_name = 'taxon/taxon_detail.html'
                context = {'taxon': obj, 'type': 'Taxon'}
            except:
                # Handle the case where no object is found
                return render(request, '404.html', status=404)

        return render(request, template_name, context)
