from django.views.generic import TemplateView
from taxon.models import Photo

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['types'] = [
            {'name': 'Fruits', 'image': '/static/images/fruit.jpg', 'url': 'url_to_fruit_list'},
            {'name': 'Vegetables', 'image': '/static/images/vegetable.jpg', 'url': 'url_to_vegetable_list'},
            {'name': 'Herbs', 'image': '/static/images/herb.jpg', 'url': 'url_to_herb_list'},
            {'name': 'Flowers', 'image': '/static/images/flowers.jpg', 'url': 'url_to_herb_list'},
            # Add other types similarly...
        ]
        return context
