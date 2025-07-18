from django.views import View
from django.http import HttpResponse
from .utils import generate_qr_code, generate_label_svg
from django.contrib import messages
from django.shortcuts import redirect
from .printing import print_label
from django.shortcuts import get_object_or_404
from farm.models import SeedLot
from django.apps import apps
from .pdf_utils import svg_to_pdf


class LabelPDFView(View):
    def get(self, request, app_label, model_name, pk):
        # Get the model and object
        model = apps.get_model(app_label, model_name)
        obj = get_object_or_404(model, pk=pk)

        # Generate SVG
        svg_content = generate_label_svg(model_name, obj, request)

        # DEBUG: Return SVG to see what we're generating
        # return HttpResponse(svg_content, content_type='image/svg+xml')

        # Convert to PDF
        pdf_data = svg_to_pdf(svg_content)

        # Return PDF response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{obj}_label.pdf"'

        return response


class GenerateQRCodeView(View):
    def get(self, request, pk):
        # Moved from farm/views.py - same logic, new home
        qr_image = generate_qr_code(pk, request, format='PNG')
        response = HttpResponse(content_type="image/png")
        response.write(qr_image)
        return response


# labels/views.py - add this

class TestLabelView(View):
    def get(self, request, pk):
        seedlot = get_object_or_404(SeedLot, pk=pk)
        svg_content = generate_label_svg('seedlot', seedlot, request)
        return HttpResponse(svg_content, content_type='image/svg+xml')


class PrintLabelView(View):
    def get(self, request, app_label, model_name, pk):
        model = apps.get_model(app_label, model_name)
        obj = get_object_or_404(model, pk=pk)

        print_label(obj, request)

        messages.success(request, f"Label printed for {obj}")
        # labels/views.py - fix the redirect
        # In PrintLabelView, instead of generic_detail:
        return redirect(f'{app_label}:{model_name}_detail', pk=pk)