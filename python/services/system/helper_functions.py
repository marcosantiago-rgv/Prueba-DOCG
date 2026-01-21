
from python.models.modelos import *
from sqlalchemy import String, Text, or_,func,Integer, Float, Numeric,text
from sqlalchemy.sql import case
from flask import session,flash,request,redirect
import re
import json
from datetime import date, datetime,timedelta
import random
from sqlalchemy import inspect
from config import *
import math
from functools import wraps

#####
# funciones auxiliares
#####

def get_all_models():
    """
    Retorna una lista de todos los modelos registrados en SQLAlchemy
    que tienen asignado el atributo __tablename__.
    """
    models = []
    for model in db.Model.registry._class_registry.values():
        if hasattr(model, "__tablename__"):
            models.append(model)
    return models

def get_model_by_name(table_name):
    """
    Retorna el modelo que corresponde al nombre de la tabla proporcionado.
    Si no se encuentra, retorna None.
    """
    for model in get_all_models():
        if model.__tablename__ == table_name:
            return model
    return None

def sanitize_data(model, data):
    for col in model.__table__.columns:
        if col.name not in data:
            continue

        value = data[col.name]
        # 🧩 1. Si viene como lista con un solo valor, tomar el primero
        if isinstance(value, list) and len(value) == 1:
            value = value[0]
        # 🧩 2. Normaliza booleans
        col_type_str = str(col.type).lower()
        if "bool" in col_type_str:
            if isinstance(value, str):
                val = value.strip().lower()
                if val in ("true", "1", "yes", "on"):
                    value = True
                elif val in ("false", "0", "no", "off", ""):
                    value = False
                else:
                    value = None
        elif "time" in col_type_str:
            if not value:
                value = None
            else:
                try:
                    # First try HH:MM
                    t = datetime.strptime(value, "%H:%M").time()
                except ValueError:
                    try:
                        # Then try HH:MM:SS
                        t = datetime.strptime(value, "%H:%M:%S").time()
                    except ValueError:
                        t = None

                value = t
        elif "date" in col_type_str:
            if not value:
                value = None
            elif isinstance(value, (datetime, date)):
                value = value if isinstance(value, date) else value.date()
            else:
                try:
                    # Try DD/MM/YYYY (SAT / MX)
                    value = datetime.strptime(value, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        # Try ISO YYYY-MM-DD
                        value = date.fromisoformat(value)
                    except ValueError:
                        value = None
        # 🧩 3. Convierte cadenas vacías según tipo
        elif value == "" or value is None:
            if any(t in col_type_str for t in ["date", "time", "timestamp", "uuid", "json"]):
                value = None
            elif any(t in col_type_str for t in ["int", "numeric", "float", "double", "real"]):
                value = None
            elif any(t in col_type_str for t in ["char", "text", "string"]):
                value = None

        # 🧩 4. Si es numérico, intenta convertirlo correctamente
        elif any(t in col_type_str for t in ["int", "numeric", "float", "double", "real"]):
            try:
                if value == "" or value is None:
                    value = None
                elif "int" in col_type_str:
                    value = int(value)
                else:
                    value = float(value)
            except (ValueError, TypeError):
                value = None  # fallback seguro
        if isinstance(value, float) and math.isnan(value):
            value = None                  
        if col_type_str=='array':
            if value is None:
                value=[]
            elif isinstance(value, str):
                value=[value]
            else:
                value=list(value)     
        data[col.name] = value
    return data

# Función auxiliar para convertir cada registro a diccionario
def record_to_dict(record):
    return {
        col: (
            getattr(record, col).isoformat()
            if hasattr(getattr(record, col), "isoformat")
            else getattr(record, col)
        )
        for col in record.__table__.columns.keys()
    }


# Filtro para formatear fechas
def date_format(value):
    if value:
        return value.strftime("%Y-%m-%d")
    else:
        return value
    
# Filtro para formatear moneda
def money_format(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return value 

def hour_format(value):
    if 'pm' in value.lower() or 'am' in value.lower():
        new_value= datetime.strptime(value.strip().lower(), "%I:%M %p").strftime("%H:%M")
    else:
        try:
            parts = value.strip().split(":")
            new_value=":".join(parts[:2])    
        except:
            new_value=value
    return new_value


def search_table(query, model, search, related_name_columns,aggregated_columns):
    filters = []

    related_name_columns = related_name_columns or []
    aggregated_columns = aggregated_columns or []

    # try to parse number
    try:
        search_number = float(search) if "." in search else int(search)
    except ValueError:
        search_number = None

    for col in model.__table__.columns:
        col_attr = getattr(model, col.name)

        if isinstance(col.type, (String, Text)):
            filters.append(col_attr.ilike(f"%{search}%"))

        elif (
            search_number is not None
            and isinstance(col.type, (Integer, Float, Numeric))
        ):
            filters.append(col_attr == search_number)

    for col in related_name_columns:
        try:
            col_type = col.type
        except AttributeError:
            continue

        if isinstance(col_type, (String, Text)):
            filters.append(col.ilike(f"%{search}%"))

        elif (
            search_number is not None
            and isinstance(col_type, (Integer, Float, Numeric))
        ):
            filters.append(col == search_number)

    for col in aggregated_columns:
        # aggregated columns are ALWAYS text
        filters.append(col.ilike(f"%{search}%"))

    if filters:
        query = query.filter(or_(*filters))

    return query

def get_id_visualizacion(table_name):
    modelo = get_model_by_name(table_name)
    max_id = modelo.query.with_entities(func.max(modelo.id_visualizacion)).scalar()       
    return (max_id or 0) + 1

# queries con variables dinamicas
PARAM_REGEX = re.compile(r":([a-zA-Z_][a-zA-Z0-9_]*)")

def extract_param_names(sql: str) -> set[str]:
    # Find :param placeholders in the SQL
    return set(PARAM_REGEX.findall(sql))

def to_jsonable(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, Decimal):
        return float(v)  # or str(v) if you prefer exact representation
    return v

def rowmapping_to_dict(rm):
    # rm is a RowMapping
    return {k: to_jsonable(v) for k, v in rm.items()}

from decimal import Decimal, InvalidOperation
import re

def parse_money(value):
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return float(str(value))
    if isinstance(value, str):
        s = value.strip()
        # remove everything except digits, decimal separators, minus sign
        s = re.sub(r'[^0-9,.\-]', '', s)

        # Handle common formats:
        # If there's a comma but no dot, treat comma as decimal sep (e.g., "45,50")
        if ',' in s and '.' not in s:
            s = s.replace('.', '').replace(',', '.')
        else:
            # Otherwise drop thousands commas (e.g., "1,234.56" -> "1234.56")
            s = s.replace(',', '')

        try:
            return float(s)
        except InvalidOperation:
            raise ValueError(f"importe value '{value}' is not a valid number")

def record_to_ordered_list(model, joins, record, columns_order):
    ordered_fields = []

    # Handle Row vs Model instance
    if hasattr(record, "_mapping"):
        record_mapping = record._mapping
        model_instance = record_mapping.get(model, record)
    else:
        record_mapping = {}
        model_instance = record
    mapper = inspect(model_instance.__class__)
    fk_map = {}

    for column in mapper.columns:
        for fk in column.foreign_keys:
            fk_map[column.name] = fk.column.table.name
    # Step 1: Base model columns
    base_data = {}
    for col in model.__table__.columns.keys():
        val = getattr(model_instance, col)
        if isinstance(val, datetime):
            if "fecha" in col.lower():
                val = (val - timedelta(hours=6))
                val = val.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(val, date):
            val = val.strftime('%Y-%m-%d')
        base_data[col] = val

    # Step 2: Add *all* join columns from record_mapping (safe types only)
    for key, value in record_mapping.items():
        if key == model:
            continue  # skip the whole model object
        if isinstance(value, datetime):
            if "fecha" in col.lower():
                value = (value - timedelta(hours=6))
                value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, date):
            value = value.strftime('%Y-%m-%d')    
        elif hasattr(value, "__table__"):  # skip ORM objects
            continue
        base_data[key] = value

    # Step 3: Build ordered output based on config
    if columns_order:
        for col in columns_order:
            # Support dotted notation: Roles.nombre -> id_rol_nombre
            if "." in col:
                table_alias, column_name = col.split(".")
                alias_field = f"id_{table_alias.lower()}_{column_name}"
                value = base_data.get(alias_field)
            else:
                if 'id_' in col and col not in ("id_visualizacion", "id_usuario_correo_electronico","id_categoria_de_gasto","id_proveedor","id_cuenta_de_banco"):
                    id_col=re.sub(r'_(nombre|descripcion|nombre_completo|id_visualizacion).*$', '', col)
                    value = f'{base_data.get(col)}__{base_data.get(id_col)}__{fk_map.get(id_col)}'
                else:
                    value = base_data.get(col)
            if value is not None and value!='None__None':
                ordered_fields.append((col, value))
    else:
        # Default: preserve order of base_data
        ordered_fields = list(base_data.items())

    return ordered_fields

def record_to_ordered_dict(model, record, columns_order):
    """
    Returns an ORDER-SAFE payload:
    [
        {
            "section": "informacion_general",
            "fields": [
                {"key": "id", "value": 1},
                {"key": "periodo", "value": "2025"}
            ]
        },
        ...
    ]
    """

    # ---------------------------
    # Handle Row vs Model instance
    # ---------------------------
    if hasattr(record, "_mapping"):
        record_mapping = record._mapping
        model_instance = record_mapping.get(model, record)
    else:
        record_mapping = {}
        model_instance = record

    mapper = inspect(model_instance.__class__)
    fk_map = {}

    for column in mapper.columns:
        for fk in column.foreign_keys:
            fk_map[column.name] = fk.column.table.name

    # ---------------------------
    # Step 1: Base model columns
    # ---------------------------
    base_data = {}

    for col in model.__table__.columns.keys():
        val = getattr(model_instance, col)

        if isinstance(val, datetime):
            if "fecha" in col.lower():
                val = (val - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(val, date):
            val = val.strftime('%Y-%m-%d')

        base_data[col] = val

    # ---------------------------
    # Step 2: Join columns
    # ---------------------------
    for key, value in record_mapping.items():
        if key == model:
            continue

        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, date):
            value = value.strftime('%Y-%m-%d')
        elif hasattr(value, "__table__"):
            continue

        base_data[key] = value

    # ---------------------------
    # Step 3: ORDER-SAFE payload
    # ---------------------------
    payload = []

    for section, columns in columns_order.items():
        fields = []

        for col in columns:
            # dotted notation
            if "." in col:
                table_alias, column_name = col.split(".")
                alias_field = f"id_{table_alias.lower()}_{column_name}"
                value = base_data.get(alias_field)

            else:
                # FK formatted fields
                if (
                    col.startswith("id_")
                    and col not in (
                        "id_visualizacion",
                        "id_usuario_correo_electronico",
                        "id_categoria_de_gasto",
                        "id_proveedor",
                        "id_cuenta_de_banco",
                    )
                ):
                    id_col = re.sub(
                        r'_(nombre|descripcion|nombre_completo|id_visualizacion).*$', 
                        '', 
                        col
                    )
                    value = f'{base_data.get(col)}__{base_data.get(id_col)}__{fk_map.get(id_col)}'
                else:
                    value = base_data.get(col)

            if value is not None and value != 'None__None':
                fields.append({
                    "key": col,
                    "value": value
                })

        payload.append({
            "section": section,
            "fields": fields
        })

    return payload


def get_query_variables_values(base_query):
    variables_query = extract_param_names(base_query)
    variables_request = {k: v for k, v in request.values.items() if k in variables_query and v != ""}
    usuario=Usuarios.query.get(session["id_usuario"])
    query_variables={
        "id_usuario":usuario.id,
    }
    for key in query_variables:
        if key in variables_query and query_variables[key] is not None:
            variables_request[key] = query_variables[key]
    return variables_request


def query_to_dict(record,model):
    if hasattr(record, "_mapping"):
        record_mapping = record._mapping
        model_instance = record_mapping.get(model, record)
    else:
        record_mapping = {}
        model_instance = record
    # Base model dict
    model_dict = {}
    for col in model_instance.__table__.columns.keys():
        val = getattr(model_instance, col)
        if isinstance(val, datetime):
            if "fecha" in col.lower():
                val = (val - timedelta(hours=6))
                val = val.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(val, date):
            val = val.strftime('%Y-%m-%d')                 
        model_dict[col] = val
    # Add all join columns (from add_columns)
    for key, value in record_mapping.items():
        # skip the full model object itself (not serializable)
        if isinstance(value, model.__class__):
            continue
        if isinstance(value, datetime):
            if "fecha" in key.lower():
                value = (value - timedelta(hours=6))
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                value = value.strftime('%Y-%m-%d')   
        elif not hasattr(value, "__table__"):  # skip whole ORM objects like Inventario
            model_dict[key] = value
    return model_dict

def generate_pin(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def resolve_foreign_keys_bulk(model, df):
    """
    Resolves all FK id_visualizacion values in a DataFrame using batch queries.
    Returns a new DataFrame with FK columns replaced by real PKs.
    """

    fk_info = []  # (local_col, RefModel, ref_pk_col)

    # --- Discover FK metadata once ---
    for column in model.__table__.columns:
        for fk in column.foreign_keys:
            local_col = column.name
            ref_table = fk.column.table.name
            ref_pk_col = fk.column.name
            RefModel = get_model_by_name(ref_table)
            if RefModel:
                fk_info.append((local_col, RefModel, ref_pk_col))

    # --- For each FK: gather distinct visual IDs → bulk query ---
    fk_maps = {}  # (RefModel, ref_pk_col) -> {visual_id: real_pk}

    for local_col, RefModel, ref_pk_col in fk_info:

        if local_col not in df.columns:
            continue

        needed_ids = (
            df[local_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if not needed_ids:
            continue

        # ONE bulk query
        rows = (
            db.session.query(RefModel.id_visualizacion, getattr(RefModel, ref_pk_col))
            .filter(RefModel.id_visualizacion.in_(needed_ids))
            .all()
        )

        fk_maps[(local_col, RefModel, ref_pk_col)] = {
            str(vis): real_pk for vis, real_pk in rows
        }

    # --- Now replace values fast (O(1) lookup, no queries) ---
    df = df.copy()

    for local_col, RefModel, ref_pk_col in fk_info:
        if local_col not in df.columns:
            continue

        key = (local_col, RefModel, ref_pk_col)
        mapping = fk_maps.get(key, {})

        # check for missing visual IDs
        missing = set(
            df[local_col].dropna().astype(str)
        ) - set(mapping.keys())

        if missing:
            raise ValueError(
                f"No se pudieron resolver los valores de la columna relacionada con la tabla '{RefModel.__tablename__}': "
                f"id inexistentes: {', '.join(missing)}"
            )

        # replace visual IDs with real PKs
        df[local_col] = (
            df[local_col]
            .astype(str)
            .map(mapping)
            .fillna(df[local_col])   # keep empty cells
        )

    return df

def detect_table_from_columns(df_columns):
    normalized = {c.strip() for c in df_columns}

    best_match = None
    best_score = 0

    for table_name, column_map in TABLE_COLUMN_MAPS.items():
        expected = set(column_map.keys())
        score = len(expected & normalized)

        if score > best_score:
            best_match = table_name
            best_score = score

    return best_match if best_score > 0 else None

def deep_getattr(obj, attr, default=None):
    try:
        for part in attr.split('.'):
            obj = getattr(obj, part)
        return obj
    except AttributeError:
        return default
    
def get_kpi(table_name, sql_name, variables):
    path = f'./static/sql/summary_kpis/{table_name}/{sql_name}.sql'
    base_query = open(path, "r", encoding="utf-8").read()
    variables_query = extract_param_names(base_query)
    variables_request = {
        k: v for k, v in variables.items()
        if k in variables_query and v != ""
    }
    result = db.session.execute(text(base_query), variables_request).fetchone()
    if not result:
        return None  # or 0, or {}
    row = dict(result._mapping)
    return next(iter(row.values()))

def return_url_redirect(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        response = f(*args, **kwargs)  # 👈 run route FIRST

        return_url = session.pop("return_url", None)
        if return_url:
            return redirect(return_url)

        return response
    return wrapper

def field_changed(changed_fields, field_name):
    if field_name in changed_fields:
        old = changed_fields[field_name]["old"]
        new = changed_fields[field_name]["new"]
        return True, old, new
    return False, None, None
