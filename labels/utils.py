import qrcode
from io import BytesIO
import base64


def generate_qr_code(uuid, request, format='PNG', size=None):
    """Generate QR code for entity UUID - uses same URL building as old GenerateQRCodeView"""
    qr_url = f"{request.scheme}://{request.get_host()}/{uuid}/"
    qr = qrcode.make(qr_url)

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
    """30256 label template for SeedLot"""
    return f'''<svg width="288" height="167" viewBox="0 0 288 167" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="288" height="167" fill="white"/>

  <text x="12" y="30" font-family="Arial, sans-serif" font-size="22" font-weight="bold" fill="black">
    {seedlot.variety.name}
  </text>

  <rect x="10" y="38" width="268" height="23" fill="black" rx="2"/>
  <text x="144" y="57" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="white" text-anchor="middle">
    {seedlot.variety.taxon.name}
  </text>

  <text x="170" y="77" font-family="Arial, sans-serif" font-size="12" fill="black" font-style="italic" text-anchor="end">
    {seedlot.variety.taxon.species_name}
  </text>

  <text x="170" y="93" font-family="Arial, sans-serif" font-size="11" fill="black" text-anchor="end">
    Source: {seedlot.origin or "Unknown"}
  </text>
  <text x="170" y="106" font-family="Arial, sans-serif" font-size="11" fill="black" text-anchor="end">
    Received: {seedlot.date_received or "Unknown"}
  </text>
  <text x="170" y="119" font-family="Arial, sans-serif" font-size="11" fill="black" text-anchor="end">
    Quantity: {seedlot.quantity or ""} {seedlot.units or ""}
  </text>

  <image x="188" y="67" width="90" height="90" href="data:image/png;base64,{qr_base64}"/>
</svg>'''


# Placeholder templates - we'll fill these in as needed
def planting_label_template(planting, qr_base64):
    return "<!-- Planting template TODO -->"


def harvest_label_template(harvest, qr_base64):
    return "<!-- Harvest template TODO -->"


def seedlingbatch_label_template(batch, qr_base64):
    return "<!-- SeedlingBatch template TODO -->"
