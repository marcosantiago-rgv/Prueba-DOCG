# python/services/system/display_values.py
"""
Helper para convertir objetos relacionados (Almacen, Usuario, etc.) en valores display-friendly (nombre, correo, id_visualizacion).
"""


from python.services.system.display_values import display_dict, display_list


def get_display_value(val):
    # Si es un objeto con atributo 'nombre', usa ese atributo
    if hasattr(val, 'nombre'):
        return getattr(val, 'nombre')
    # Si es un objeto con atributo 'id_visualizacion', usa ese atributo
    if hasattr(val, 'id_visualizacion'):
        return getattr(val, 'id_visualizacion')
    # Si es un objeto con atributo 'correo_electronico', usa ese atributo
    if hasattr(val, 'correo_electronico'):
        return getattr(val, 'correo_electronico')
    # Si es un objeto, conviértelo a string (por si acaso)
    if hasattr(val, '__class__') and not isinstance(val, (str, int, float, type(None))):
        return str(val)
    return val


def display_dict(data):
    """
    Recibe un diccionario y reemplaza los valores que sean objetos por su display value.
    """
    return {k: get_display_value(v) for k, v in data.items()}


def display_list(data):
    """
    Recibe una lista y reemplaza los valores que sean objetos por su display value.
    """
    return [get_display_value(v) for v in data]


def get_summary_display_data(record, variables):
    """
    Arma los datos de resumen para la plantilla, usando display_dict para que los valores sean legibles.
    """
    primary = variables.get('primary') or []
    primary_info = display_list(
        [deep_getattr(record, detail) for detail in primary])
    record_data = {}
    data = variables.get('data', {})
    for section, details in data.items():
        record_data[section] = display_dict({
            detail: deep_getattr(record, detail)
            for detail in details
        })
    return primary_info, record_data
