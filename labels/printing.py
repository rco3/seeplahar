import subprocess
import tempfile
import os
from .utils import generate_label_svg


def print_label(entity, request, printer_name='DYMO_LabelWriter_450'):
    """Print label for any entity - printer_name hardcoded for testing"""
    entity_type = entity._meta.model_name
    svg_content = generate_label_svg(entity_type, entity, request)
    print_svg_to_dymo450(svg_content, printer_name)


def print_svg_to_dymo450(svg_content, printer_name):
    """Convert SVG to PNG and send to Dymo 450"""
    with tempfile.NamedTemporaryFile(suffix='.svg', mode='w', delete=False) as svg_file:
        svg_file.write(svg_content)
        svg_file.flush()

        try:
            # Convert SVG to PNG at exact label dimensions
            png_path = svg_file.name.replace('.svg', '.png')
            subprocess.run([
                'rsvg-convert',
                '-w', '1106',
                '-h', '624',
                '-o', png_path,
                svg_file.name
            ], check=True)

            # In print_svg_to_dymo450, after the rsvg-convert:
            subprocess.run(['file', png_path])  # This will show actual PNG dimensions

            # Print to your actual Dymo
            subprocess.run([
                'lpr',
                '-P', printer_name,
                '-o', 'media=30256',
                '-o', 'PrintDensity=Medium',
                '-o', 'ppi=300',
                # '-o', 'PrintQuality=Graphics',
                png_path
            ], check=True)

        finally:
            # Clean up temp files
            os.unlink(svg_file.name)
            if os.path.exists(png_path):
                os.unlink(png_path)