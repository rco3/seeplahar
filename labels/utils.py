import qrcode
from io import BytesIO
import base64


def generate_qr_code(uuid, request, format='PNG', size=None):
    """Generate QR code for entity UUID - uses same URL building as old GenerateQRCodeView"""
    qr_url = f"{request.scheme}://{request.get_host()}/{uuid}/"

    # Create QR code with no border
    qr_code = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,  # Remove the quiet zone
    )
    qr_code.add_data(qr_url)
    qr_code.make(fit=True)
    qr = qr_code.make_image(fill_color="black", back_color="white")

    if size:
        qr = qr.resize(size)

    if format == 'base64':
        buffer = BytesIO()
        qr.save(buffer, "PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    elif format == 'PIL':
        return qr
    else:  # PNG bytes
        buffer = BytesIO()
        qr.save(buffer, format)
        buffer.seek(0)
        return buffer.read()


def generate_label_svg(entity_type, entity, request):
    """Generate SVG for any entity type"""
    qr_base64 = generate_qr_code(entity.id, request, format='base64')

    templates = {
        'seedlot': seedlot_label_template,
        'planting': planting_label_template,
        'harvest': harvest_label_template,
        'seedlingbatch': seedlingbatch_label_template,
    }

    template_func = templates.get(entity_type)
    if not template_func:
        raise ValueError(f"No template for entity type: {entity_type}")

    return template_func(entity, qr_base64)


def seedlot_label_template(seedlot, qr_base64):
    """30256 label - 1106x624 usable area with characteristics and smaller QR"""

    # Get variety characteristics
    characteristics = []
    for char_value in seedlot.variety.characteristicvalue_set.all():
        characteristics.append(f"{char_value.characteristic.name}: {char_value.value}")

    # Build characteristics text elements
    char_lines = ""
    for i, char in enumerate(characteristics[:8]):  # Max 8 lines to fit
        y_pos = 280 + (i * 40)
        if y_pos < 570:  # Don't run into bottom
            char_lines += f'<text x="8" y="{y_pos}" font-family="Arial, sans-serif" font-size="36" fill="black">{char}</text>\n  '

    return f'''<svg width="1106" height="624" viewBox="0 0 1106 624" xmlns="http://www.w3.org/2000/svg">

  <!-- Variety name -->
  <text x="8" y="90" font-family="Arial, sans-serif" font-size="100" font-weight="bold" fill="black">
    {seedlot.variety.name}
  </text>

  <!-- Taxon bar - FULL usable width -->
  <rect x="0" y="105" width="1106" height="85" fill="black"/>
  <text x="553" y="171" font-family="Arial, sans-serif" font-size="75" font-weight="bold" fill="white" text-anchor="middle">
    {seedlot.variety.taxon.name}
  </text>

  <!-- Species -->
  <text x="553" y="230" font-family="Arial, sans-serif" font-size="45" fill="black" font-style="italic" text-anchor="middle">
    {seedlot.variety.taxon.species_name}
  </text>

  <!-- Variety characteristics - left side -->
  {char_lines}

  <!-- SeedLot details - right side, right justified -->
  <text x="1098" y="280" font-family="Arial, sans-serif" font-size="42" fill="black" text-anchor="end">
    Source: {seedlot.origin or "Unknown"}
  </text>
  <text x="1098" y="325" font-family="Arial, sans-serif" font-size="42" fill="black" text-anchor="end">
    Received: {seedlot.date_received or "Unknown"}
  </text>
  <text x="1098" y="370" font-family="Arial, sans-serif" font-size="42" fill="black" text-anchor="end">
    Quantity: {seedlot.quantity or ""} {seedlot.units or ""}
  </text>

  <!-- QR code - smaller, bottom right -->
  <image x="866" y="381" width="240" height="243" href="data:image/png;base64,{qr_base64}"/>
</svg>'''

# Placeholder templates - we'll fill these in as needed
def planting_label_template(planting, qr_base64):
    return "<!-- Planting template TODO -->"


def harvest_label_template(harvest, qr_base64):
    return "<!-- Harvest template TODO -->"


def seedlingbatch_label_template(batch, qr_base64):
    return "<!-- SeedlingBatch template TODO -->"
