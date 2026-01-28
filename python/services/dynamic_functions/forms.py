from python.models.modelos import *
from sqlalchemy import func
from python.services.system.helper_functions import *
from flask import jsonify
from datetime import timedelta
from python.services.dynamic_functions.input_tables import *
from python.services.dynamic_functions.double_tables import *

# Es  para decirle que cuando entre al formulario y encuentre estas variables genere un dropdown con los datos o valores que estan aqui


def get_foreign_options():
    foreign_options = {
        "id_rol": Roles.query.filter_by(estatus="Activo"),
        "id_categoria_de_reporte": CategoriasDeReportes.query.filter_by(estatus="Activo"),

        "id_producto": Productos.query.filter_by(estatus="Activo"),
        "id_proveedor": Proveedores.query.filter_by(estatus="Activo"),
        "proveedores": Proveedores.query.filter_by(estatus="Activo"),
        "unidad_de_medida": {"Pieza", "KG"},
        "dias_de_entrega": ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],

        "id_producto": Productos.query.filter_by(estatus="Activo"),
        # solomostrara todos los almacenes activos en el dropdown
        "id_almacen": Almacen.query.filter_by(estatus="Activo"),
        # solomostrara los almacenes origen activos en el dropdown
        "id_almacen_origen": Almacen.query.filter_by(estatus="Activo"),
        # solomostrara los almacenes destino activos en el dropdown
        "id_almacen_destino": Almacen.query.filter_by(estatus="Activo"),
        "id_proveedor": Proveedores.query.filter_by(estatus="Activo"),
        "proveedores": Proveedores.query.filter_by(estatus="Activo"),
        # "id_ubicacion": Ubicaciones.query.filter_by(estatus="Activo"),
        "unidad_de_medida": {"Pieza", "KG"},
        "dias_de_entrega": ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Domingo"],
        "id_categoria": CategoriaGasto.query.filter_by(estatus="Activo"),

        "id_gasto": Gasto.query.filter(Gasto.estatus != "Pagado"),
        "id_cuenta": CuentaBanco.query.filter_by(estatus="Activo"),


        "id_orden_de_compra": OrdenesDeCompra.query.filter(OrdenesDeCompra.estatus != "Cancelado")
    }

    return foreign_options


# specific filters for forms
# specific filters for forms
def get_form_options(table_name):
    options = {
        # "inventario": {"id_producto": Productos.query.filter(Productos.estatus == "Activo",Productos.categoria.has(CategoriasDeProductos.nombre.in_(["Producto terminado", "Producto intermedio"])))},
    }
    options = options.get(table_name, {})
    return options


# permite hacer varias selecciones en el dropdown de un formulario
def get_multiple_choice_data():
    multiple_choice_data = {}
    options = {
        # en este caso cuando crear proveedores sale el dropdown dias de entrega
        "dias_de_entrega": ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'],
    }
    for i in options:
        multiple_choice_data[i] = {
            "selected": [],
            "options": options[i]
        }
    return multiple_choice_data


# le dices que campos ignore y no los muestre en el formulario de agregar o editar
def get_ignored_columns(table_name):
    columnas_generales = {'fecha_de_creacion', 'estatus', 'id_usuario',
                          'id_visualizacion', 'fecha_de_actualizacion', 'id_usuario'}
    columns = {
        "usuarios": {'codigo_unico', 'contrasena', 'contrasena_api', 'intentos_de_inicio_de_sesion', 'ultima_sesion', 'ultimo_cambio_de_contrasena', 'codigo_unico_expira', 'codigo_unico_login'},
        "archivos": {'tabla_origen', 'id_registro', 'nombre', 'ruta_s3'},
        "ordenes_de_compra": {'importe_total', 'subtotal', 'descuentos', 'fecha_entrega_real'},

        # "almacen": set(),
        # "productos_inventario": set(),

        # En transferencia de inventario ya no ocultamos el almacén de origen
        # para evitar que el campo requerido quede en NULL al guardar
        # "transferencia_inventario": set(),

        "cuenta_banco": {'saldo_actual'},
        "pago": {'monto'}

    }
    columns = columns.get(table_name, columnas_generales) | columnas_generales
    return columns

# le dices que campos ignore y no los muestre en el formulario de editar


def get_ignored_columns_edit(table_name, estatus):
    columnas_generales = {'default': {'fecha_de_creacion',
                                      'id_usuario', 'id_visualizacion', 'fecha_de_actualizacion'}}
    tables = {
        "usuarios": {'default': {'codigo_unico', 'contrasena', 'contrasena_api', 'intentos_de_inicio_de_sesion', 'ultima_sesion', 'ultimo_cambio_de_contrasena', 'codigo_unico_expira', 'codigo_unico_login'}},
        "archivos": {'default': {'tabla_origen', 'id_registro', 'nombre', 'ruta_s3'}},
        "ordenes_de_compra": {'default': {'importe_total', 'importe_pagado', 'subtotal', 'descuentos', 'estatus_de_pago', 'fecha_entrega_real'}},
        "cuenta_banco": {'default': {'saldo_actual'}},

    }
    table_dict = tables.get(table_name, columnas_generales)
    if not estatus or estatus not in table_dict:
        estatus = 'default'
    columns = table_dict.get(estatus, set()) | columnas_generales['default']
    if table_name in ('ejemplo'):
        columns = columns-{'estatus'}
    return columns


# Aqui le dices que variables ya no son obligatorias en el formulario de agregar o editar ya no deberia aparcer el * en el formulario
def get_non_mandatory_columns(table_name):
    columnas_generales = {'descripcion', 'notas', 'fecha_fin'}
    columns = {
        "productos": {'marca', 'codigo_de_barras'} | columnas_generales,
        "proveedores": {'telefono', 'email', 'direccion', 'codigo_postal', 'pais', 'persona_contacto', 'telefono_contacto', 'email_contacto', 'condiciones_de_pago', 'rfc', 'razon_social', 'sitio_web', 'condiciones_pago'} | columnas_generales,
        "productos_inventario": {'marca', 'codigo_de_barras'} | columnas_generales,
        "almacen": {'descripcion'} | columnas_generales,
        "transferencia_inventario": set() | columnas_generales,

    }
    columns = columns.get(table_name)
    if columns == None:
        columns = columnas_generales
    return columns


# Aqui le dices que variables van a tener un valor por default al momento de crear un nuevo registro
def get_default_variable_values(table_name):
    default_values = {
        "ordenes_de_compra": {"fecha_orden": datetime.today().strftime("%Y-%m-%d"), "descuentos": 0},
    }
    default_values = default_values.get(table_name, {})
    return default_values


# Aqui le dices a donde redirigir despues de agregar un nuevo registro
def get_url_after_add(table_name):

    columns = {
        "ordenes_de_compra": "dynamic.double_table_view",
        "pago": "dynamic.double_table_view",
        # le decimos que despues de agregar la cabcera de transferencia de inventario redirija al double table view para agregar los productos a transferir
        "transferencia_inventario": "dynamic.double_table_view",
    }
    return columns.get(table_name, 'dynamic.table_view')


# def get_non_edit_status(table_name=None):
#     if table_name in ['pago', 'gasto']:
#         return ['Cancelado', 'Pagado']
#     status = ['Cancelado', 'Cancelada', 'Recibida', 'Finalizada', 'Entregada', 'Realizada', 'Realizado',
#               'Pagado', 'Pagado parcial', 'Aprobada', 'Aprobado', 'Recibida parcial', 'Pagado parcial', 'En proceso']
# Aqui lke dices los estatus en los que no se podra editar un registro cuando tengan estos estatus ya registrados
def get_non_edit_status(table_name):
    general_status = {'Cancelado', 'Cancelada', 'Recibida', 'Finalizada', 'Entregada', 'Realizada', 'Realizado',
                      'Pagado', 'Pagado parcial', 'Aprobada', 'Aprobado', 'Recibida parcial', 'Pagado parcial', 'En proceso'}
    status_to_remove = {
        "table_name": {'estatus'},
    }
    status = general_status-status_to_remove.get(table_name, {''})
    return status


def get_no_edit_access():  # Aqui le dices en que tablas no se permitira editar ningun registro sin importar el estatus que tengan

    tables = ['productos_en_ordenes_de_compra', 'productos_en_ordenes_de_ventas', 'entrega_de_productos_en_ordenes_de_compra',
              'recetas', 'gastos_y_compras_en_pagos', 'productos_en_transferencias_de_inventario']
    return tables


# filtrar el valor de un valor ejemplo proveedor solo muestre ubuicacuibes actuivas de esse proveedor
def get_form_filters(table_name):
    filters = {
        "nombre_de_tabla": {'id_a_filtrar': 'id_filtro'},
    }
    filters = filters.get(table_name, '')
    return filters


def get_parent_record(table_name):
    parent_record = {
        "productos_en_ordenes_de_compra": 'id_orden_de_compra',
    }
    parent_record = parent_record.get(table_name, '')
    return parent_record


def get_parent_record(table_name, parent_table):
    parent_record = {
        "productos_en_ordenes_de_compra": {'ordenes_de_compra': 'id_orden_de_compra'},
    }
    parent_record = parent_record.get(
        table_name, {'': ''}).get(parent_table, '')
    return parent_record
