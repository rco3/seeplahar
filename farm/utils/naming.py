# farm/utils/naming.py
import re


def abbreviate_name(name, max_length=10):
    """
    Create abbreviation from name: first 3 letters of each word, max length

    Examples:
        'Rebel Starfighter Prime' -> 'RebStaPri'
        'Wild Boar Farms' -> 'WilBoaFar'
        'Cherokee Purple' -> 'CherPur'

    Args:
        name (str): The name to abbreviate
        max_length (int): Maximum length of abbreviation (default: 10)

    Returns:
        str: Abbreviated name with proper capitalization
    """
    if not name:
        return 'Unk'

    # Split on spaces and punctuation, remove empty strings
    words = [w for w in re.split(r'[^\w]+', name) if w]

    # Take first 3 letters of each word
    parts = []
    for word in words:
        if len(word) >= 3:
            parts.append(word[:3])
        else:
            parts.append(word)

    # Join and truncate to max_length
    abbrev = ''.join(parts)[:max_length]

    # Capitalize first letter of each original word part
    result = ''
    char_count = 0
    for word in words:
        if char_count >= len(abbrev):
            break
        word_len = min(3, len(word), len(abbrev) - char_count)
        if word_len > 0:
            result += abbrev[char_count].upper() + abbrev[char_count + 1:char_count + word_len].lower()
            char_count += word_len

    return result or 'Unk'


def get_next_serial(model_class, customer, base_name, field_name='name'):
    """
    Find the next available serial number for a given base name pattern.

    Args:
        model_class: The Django model class to search
        customer: The customer instance for filtering
        base_name (str): The base name pattern (e.g., 'RebStaPriWilBoaFar')
        field_name (str): The field name to search in (default: 'name')

    Returns:
        str: Next available serial in format '01', '02', etc.
    """
    # Find all existing records with this base name pattern
    filter_kwargs = {
        'customer': customer,
        f'{field_name}__startswith': base_name,
        f'{field_name}__regex': rf'^{re.escape(base_name)}\d{{2}}$'
    }

    existing_names = model_class.objects.filter(**filter_kwargs).values_list(field_name, flat=True)

    # Extract serial numbers
    used_serials = set()
    for name in existing_names:
        if len(name) >= 2 and name[-2:].isdigit():
            used_serials.add(int(name[-2:]))

    # Find first available serial (01-99)
    for serial in range(1, 100):
        if serial not in used_serials:
            return f"{serial:02d}"

    # If all serials 01-99 are used, return 00
    return "00"


def generate_entity_name(variety_name, source_name, model_class, customer, max_total_length=22):
    """
    Generate a standardized entity name using variety and source.

    Args:
        variety_name (str): Name of the variety
        source_name (str): Name of the source (partner, vendor, etc.)
        model_class: Django model class for checking existing names
        customer: Customer instance for filtering
        max_total_length (int): Maximum total name length (default: 22)

    Returns:
        str: Generated name like 'RebStaPriWilBoaFar01'
    """
    if not variety_name:
        variety_name = 'Unknown'
    if not source_name:
        source_name = 'Unknown'

    # Get abbreviations
    variety_abbrev = abbreviate_name(variety_name, max_length=10)
    source_abbrev = abbreviate_name(source_name, max_length=10)

    # Ensure total length doesn't exceed max (including 2-digit serial)
    max_base_length = max_total_length - 2
    base_length = len(variety_abbrev) + len(source_abbrev)

    if base_length > max_base_length:
        # Truncate proportionally
        variety_max = min(len(variety_abbrev), max_base_length // 2)
        source_max = max_base_length - variety_max
        variety_abbrev = variety_abbrev[:variety_max]
        source_abbrev = source_abbrev[:source_max]

    # Create base name and get serial
    base_name = f"{variety_abbrev}{source_abbrev}"
    serial = get_next_serial(model_class, customer, base_name)

    return f"{base_name}{serial}"