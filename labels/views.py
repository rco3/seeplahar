from django.views import View
from django.http import HttpResponse
from .utils import generate_qr_code

class GenerateQRCodeView(View):
    def get(self, request, pk):
        # Moved from farm/views.py - same logic, new home
        qr_image = generate_qr_code(pk, request, format='PNG')
        response = HttpResponse(content_type="image/png")
        response.write(qr_image)
        return response
