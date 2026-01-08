from datetime import datetime,timedelta
from flask import session
from config import *

# Filtro para formatear números con comas
def commafy(value):
    if value:
        return f"{round(value, 2):,}"
    else:
        return 0

# Filtro para formatear nombres de bases
def title_format(value):
    replacements = TITLE_FORMATS
    
    # First check for exact match
    if value=='id_visualizacion':
        return "ID"
    if value in replacements:
        if 'id' in value:
            return replacements[value]  
        return replacements[value].capitalize()
    # Replace underscores with spaces
    
    formatted = value.replace("_id_visualizacion","").replace("_", " ")
    # Remove "id " prefix if present
    if formatted.startswith("id "):
        formatted = formatted[3:]
    # Capitalize first letter
    formatted = formatted.capitalize()
    # Replace words with their accented versions if they exist
    for k, v in replacements.items():
        if k in formatted.lower():
            formatted = formatted.lower().replace(k, v.capitalize())
    return formatted.capitalize()

# Filtro para formatear nombres de bases
def money_format(value):
    return f"${round(value, 2):,}"

def remove_numbers(value):
    # Convert the value to a string (in case it's a number) and remove all digits
    return ''.join([char for char in str(value) if not char.isdigit()])
def date_format(value):
    if value:
        return value.strftime("%Y-%m-%d")
    else:
        return value
    
def can_access(path):
    return any(path.startswith(r) for r in session.get("accessible_routes", []))

def local_time(value):
    if not value:
        return ''
    try:
        if isinstance(value, str) and "Fecha hora: " in value:
            value=value.replace('Fecha hora: ', '').strip()
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            value=(value - timedelta(hours=6)).strftime('%Y-%m-%dT%H:%M')
            return 'Fecha hora: '+value
        else:
            return (value - timedelta(hours=6)).strftime('%Y-%m-%dT%H:%M')
    except Exception as e:
        return ''
