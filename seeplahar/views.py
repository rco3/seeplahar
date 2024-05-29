from django.views.generic import TemplateView
from taxon.models import Photo
from django.urls import reverse_lazy


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = [
            {
                'name': 'Fruits',
                'url': reverse_lazy('taxon:fruit-list'),
                'image': '/static/images/fruit.jpg'
            },
            {
                'name': 'Vegetables',
                'url': reverse_lazy('taxon:vegetable-list'),
                'image': '/static/images/vegetable.jpg'
            },
            {
                'name': 'Herbs',
                'url': reverse_lazy('taxon:herb-list'),
                'image': '/static/images/herb.jpg'
            },
            {
                'name': 'Flowers',
                'url': reverse_lazy('taxon:flower-list'),
                'image': '/static/images/flower.jpg'
            },
        ]
        return context
