# labels/pdf_utils.py
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.graphics import renderPDF
from io import BytesIO
import tempfile
import os


def svg_to_pdf(svg_content):
    """Convert SVG to PDF using rsvg-convert (same as thermal printing)"""

    print(f"Starting PDF conversion with SVG length: {len(svg_content)}")

    try:
        import subprocess
        import tempfile
        import os

        # Use rsvg-convert (same tool as thermal printing)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as svg_file:
            svg_file.write(svg_content)
            svg_file.flush()

            try:
                # Convert SVG to PDF directly
                pdf_path = svg_file.name.replace('.svg', '.pdf')
                subprocess.run([
                    'rsvg-convert',
                    '-f', 'pdf',
                    '-w', '1100',
                    '-h', '620',
                    '-d', '300',  # Same DPI as thermal printing
                    '-p', '300',
                    '-o', pdf_path,
                    svg_file.name
                ], check=True)

                # Read the PDF file
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()

                print(f"PDF generated, size: {len(pdf_data)} bytes")
                return pdf_data

            finally:
                # Clean up temp files
                os.unlink(svg_file.name)
                if os.path.exists(pdf_path):
                    os.unlink(pdf_path)

    except Exception as e:
        print(f"rsvg-convert failed: {e}")
        return create_simple_fallback_pdf()


def create_simple_fallback_pdf():
    """Create a simple fallback PDF if all conversions fail"""
    buffer = BytesIO()
    page_size = (4 * inch, 2.3125 * inch)
    pdf_canvas = canvas.Canvas(buffer, pagesize=page_size)

    # Add error message
    pdf_canvas.setFont("Helvetica", 12)
    pdf_canvas.drawString(36, 100, "Label generation failed")
    pdf_canvas.drawString(36, 80, "SVG conversion not available")

    pdf_canvas.save()
    buffer.seek(0)
    return buffer.getvalue()