import subprocess
import tempfile
import os
import logging
from .utils import generate_label_svg

logger = logging.getLogger(__name__)


class PrintingError(Exception):
    """Raised when label printing fails. Message is safe to show the user."""


def get_printer_name(customer=None):
    """Return the CUPS printer name. Falls back to the default if not configured."""
    from users.models import CustomerSetting
    if customer:
        name = CustomerSetting.get(customer, 'dymo_printer_name')
        if name:
            return name
    return 'DYMO_LabelWriter_450'


def list_printers():
    """Return list of available CUPS printer names, or [] on error."""
    try:
        result = subprocess.run(
            ['lpstat', '-p'],
            capture_output=True, text=True, timeout=5,
        )
        printers = []
        for line in result.stdout.splitlines():
            if line.startswith('printer '):
                printers.append(line.split()[1])
        return printers
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def diagnose():
    """Return a dict of diagnostic information for the label printing pipeline."""
    info = {}

    # rsvg-convert
    try:
        r = subprocess.run(['rsvg-convert', '--version'], capture_output=True, text=True, timeout=5)
        info['rsvg_convert'] = r.stdout.strip() or 'installed (no version output)'
    except FileNotFoundError:
        info['rsvg_convert'] = 'NOT FOUND — install with: brew install librsvg'
    except subprocess.TimeoutExpired:
        info['rsvg_convert'] = 'timeout'

    # CUPS / lpr
    try:
        r = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, timeout=5)
        info['printers'] = r.stdout.strip() or '(no printers found)'
    except FileNotFoundError:
        info['printers'] = 'lpstat NOT FOUND — CUPS not installed'
    except subprocess.TimeoutExpired:
        info['printers'] = 'timeout'

    return info


def print_label(entity, request, printer_name=None):
    """Print label for any entity to the configured Dymo printer."""
    if printer_name is None:
        customer = getattr(request.user, 'customer', None)
        printer_name = get_printer_name(customer)

    entity_type = entity._meta.model_name
    svg_content = generate_label_svg(entity_type, entity, request)
    _print_svg_to_dymo450(svg_content, printer_name)


def _check_printer_ready(printer_name):
    """Raise PrintingError if the printer is offline or not found."""
    try:
        result = subprocess.run(
            ['lpstat', '-p', printer_name],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return  # can't check, proceed and let lpr fail

    output = result.stdout + result.stderr
    if result.returncode != 0 or not output.strip():
        available = list_printers()
        raise PrintingError(
            f'Printer "{printer_name}" not found in CUPS. '
            f'Available: {available or ["(none)"]}'
        )
    if 'offline' in output.lower():
        raise PrintingError(
            f'Printer "{printer_name}" is offline. '
            f'Check that the printer and its host are powered on and reachable.'
        )
    if 'disabled' in output.lower():
        raise PrintingError(f'Printer "{printer_name}" is disabled in CUPS.')


def _print_svg_to_dymo450(svg_content, printer_name):
    """Convert SVG to PNG and send to Dymo 450 via CUPS."""
    _check_printer_ready(printer_name)

    svg_path = None
    png_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.svg', mode='w', delete=False) as f:
            f.write(svg_content)
            svg_path = f.name
        png_path = svg_path.replace('.svg', '.png')

        # Convert SVG → PNG
        result = subprocess.run(
            ['rsvg-convert', '-w', '1106', '-h', '624', '-o', png_path, svg_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            logger.error('rsvg-convert failed: %s', result.stderr)
            raise PrintingError(f'SVG→PNG conversion failed: {result.stderr.strip() or "unknown error"}')

        logger.info('rsvg-convert ok: %s', png_path)

        # Send to printer
        result = subprocess.run(
            ['lpr', '-P', printer_name, '-o', 'PageSize=w167h288',
             '-o', 'DymoPrintDensity=Normal', '-o', 'Resolution=300dpi', png_path],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            logger.error('lpr failed (printer=%s): %s', printer_name, result.stderr)
            available = list_printers()
            hint = f' Available printers: {available}' if available else ''
            raise PrintingError(
                f'Print job rejected by CUPS (printer "{printer_name}").{hint}\n{result.stderr.strip()}'
            )

        logger.info('Print job sent to %s', printer_name)

    except FileNotFoundError as e:
        missing = str(e)
        if 'rsvg-convert' in missing:
            raise PrintingError('rsvg-convert not found. Install with: brew install librsvg')
        if 'lpr' in missing:
            raise PrintingError('lpr not found. CUPS does not appear to be installed.')
        raise PrintingError(f'Command not found: {missing}')

    finally:
        if svg_path and os.path.exists(svg_path):
            os.unlink(svg_path)
        if png_path and os.path.exists(png_path):
            os.unlink(png_path)