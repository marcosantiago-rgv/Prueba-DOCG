from python.models.modelos import *
from sqlalchemy import func
from python.services.system.helper_functions import *
from flask import jsonify
from datetime import timedelta
from python.services.dynamic_functions.input_tables import *
from python.services.dynamic_functions.double_tables import *


def get_joins():
    joins = {
        "id_usuario": (Usuarios, Usuarios.id, Usuarios.nombre),
        "id_rol": (Roles, Roles.id, Roles.nombre),
        "id_categoria_de_reporte": (CategoriasDeReportes, CategoriasDeReportes.id, CategoriasDeReportes.nombre),

        "id_producto": (Productos, Productos.id, Productos.nombre),
        "id_proveedor": (Proveedores, Proveedores.id, Proveedores.nombre),
        "id_orden_de_compra": (OrdenesDeCompra, OrdenesDeCompra.id, OrdenesDeCompra.id_visualizacion),
        "id_almacen": (Almacen, Almacen.id, Almacen.nombre),
        "id_almacen_origen": (Almacen, Almacen.id, Almacen.nombre),
        "id_almacen_destino": (Almacen, Almacen.id, Almacen.nombre),
        # "id_ubicacion": (Ubicaciones, Ubicaciones.id, Ubicaciones.nombre),
        "id_gasto": (Gasto, Gasto.id, Gasto.descripcion),
        "id_categoria": (CategoriaGasto, CategoriaGasto.id, CategoriaGasto.nombre),
        "id_cuenta": (CuentaBanco, CuentaBanco.id, CuentaBanco.nombre),

    }
    return joins


def get_columns(table_name, section):
    columns = {
        "logs_auditoria": {
            "main_page": ["tabla", "id_registro", 'usuario', 'accion', 'datos_anteriores', 'datos_nuevos', 'fecha'],
            "modal": {"informacion_general": ["tabla", "id_registro", "usuario", "accion", "fecha"], "detalles": ["datos_anteriores", "datos_nuevos"]},
            "pdf": []
        },
        "rutas": {
            "main_page": ['categoria', "nombre", 'ruta'],
            "modal": {"informacion_general": ["id", "categoria", "nombre", "ruta"], "sistema": ["fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": []
        },
        "roles": {
            "main_page": ["id_visualizacion", "nombre", "estatus"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "nombre", "estatus"], "sistema": ["fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": []
        },
        "usuarios": {
            "main_page": ["id_visualizacion", "nombre", "correo_electronico", 'intentos_de_inicio_de_sesion', 'ultima_sesion', 'ultimo_cambio_de_contrasena', "estatus"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "nombre", "correo_electronico", "estatus"], "seguridad": ["contrasena_api"], "sistema": ["fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": []
        },
        "categorias_de_reportes": {
            "main_page": ["id_visualizacion", "nombre", "estatus"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "nombre", "estatus"], "sistema": ["fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": []
        },
        "reportes": {
            "main_page": ["id_visualizacion", "id_categoria_de_reporte_nombre", "nombre", "descripcion"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "id_categoria_de_reporte_nombre", "nombre", "descripcion"], "sistema": ["fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": []
        },
        "archivos": {
            "main_page": ["nombre", "nombre_del_archivo"],
            "modal": {"informacion_general": ["id", "tabla_origen", "nombre"], "detalles": ["nombre_del_archivo", "ruta_s3"], "sistema": ["fecha_de_creacion"]},
            "pdf": []
        },

        "almacen": {
            # Lo que se muestra en la tabla principal
            "main_page": ["id_visualizacion", "nombre", "ubicacion", "descripcion", "estatus"],
            # Campos que se ven en el modal
            "modal": [
                "id",
                "id_visualizacion",
                "nombre",
                "ubicacion",
                "descripcion",
                "estatus",
                "id_usuario",
                "fecha_de_creacion",
                "fecha_de_actualizacion",
            ],
            "pdf": ["nombre", "ubicacion", "descripcion", "estatus"],
        },

        "existencias": {
            "main_page": [
                "id_visualizacion",
                "id_producto_nombre",
                "id_almacen_nombre",
                "cantidad",
            ],
            "modal": [
                "id",
                "id_visualizacion",
                "id_producto_nombre",
                "id_almacen_nombre",
                "cantidad",
                # "id_usuario",
                "fecha_de_creacion",
                "fecha_de_actualizacion",
            ],
            "pdf": [
                "id_producto_nombre",
                "id_almacen_nombre",
                "cantidad",
            ],
        },

        "productos": {
            "main_page": ["id_visualizacion", "nombre", "unidad_de_medida", "estatus", "id_usuario_correo_electronico"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "nombre", "unidad_de_medida", "numero_de_usos", "codigo_de_barras", "id_archivo_imagen", "estatus"], "detalles": ["descripcion"], "sistema": ["id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": ["id_visualizacion", "nombre", "unidad_de_medida", "codigo_de_barras", "descripcion", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },
        "proveedores": {

            "main_page": ["id_visualizacion", "nombre", "razon_social", "persona_contacto", "telefono_contacto", "email_contacto", "estatus", "id_producto", "dias_de_entrega"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "nombre", "razon_social", "rfc", "direccion", "codigo_postal", "condiciones_pago", "sitio_web", "estatus"], "contacto": ["telefono", "email", "persona_contacto", "telefono_contacto", "email_contacto"], "sistema": ["id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": ["id_visualizacion", "nombre", "razon_social", "rfc", "direccion", "codigo_postal", "telefono", "email", "persona_contacto", "telefono_contacto", "email_contacto", "condiciones_pago", "sitio_web", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },

        "transferencia_inventario": {
            "main_page": [
                "id_visualizacion",
                "id_producto_nombre",
                "id_almacen_origen_nombre",
                "id_almacen_destino_nombre",
                "cantidad",
                "fecha",
                "estatus",
            ],
            "modal": [
                "id",
                "id_visualizacion",
                "id_producto_nombre",
                "id_almacen_origen_nombre",
                "id_almacen_destino_nombre",
                "cantidad",
                "fecha",
                "estatus",
                "id_usuario",
                "fecha_de_creacion",
                "fecha_de_actualizacion",
            ],
            "pdf": [
                "id_visualizacion",
                "id_producto_nombre",
                "id_almacen_origen_nombre",
                "id_almacen_destino_nombre",
                "cantidad",
                "fecha",
                "estatus",
            ],
        },
        "ordenes_de_compra": {
            "main_page": ["id_visualizacion", "id_proveedor_nombre", "fecha_orden", "fecha_entrega_estimada", "fecha_entrega_real", "importe_total", "notas", "estatus"],
            "modal": {"informacion_general": ["id", "id_visualizacion", "id_proveedor_nombre", "fecha_orden", "fecha_entrega_estimada", "fecha_entrega_real", "estatus"], "financiero": ["subtotal", "descuentos", "importe_total"], "detalles": ["notas"], "sistema": ["id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": ["id_visualizacion", "id_proveedor_nombre", "fecha_orden", "fecha_entrega_estimada", "fecha_entrega_real", "subtotal", "descuentos", "importe_total", "notas", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },
        "productos_en_ordenes_de_compra": {
            "main_page": ["id_orden_de_compra_id_visualizacion", "id_producto_nombre", "cantidad_ordenada", "cantidad_recibida", "precio_unitario", "subtotal", "descuento_porcentaje", "importe_total", "fecha_entrega_estimada", "notas", "estatus"],
            "modal": {"informacion_general": ["id", "id_orden_de_compra_id_visualizacion", "id_producto_nombre", "cantidad_ordenada", "cantidad_recibida", "fecha_entrega_estimada", "estatus"], "financiero": ["precio_unitario", "subtotal", "descuento_porcentaje", "importe_total"], "detalles": ["notas", "archivo_cotizacion"], "sistema": ["id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": ["id_orden_de_compra", "id_producto_nombre", "cantidad_ordenada", "cantidad_recibida", "precio_unitario", "subtotal", "descuento_porcentaje", "importe_total", "fecha_entrega_estimada", "notas", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },
        "entrega_de_productos_en_ordenes_de_compra": {
            "main_page": ["cantidad_recibida", "fecha_entrega"],
            "modal": {"informacion_general": ["id", "cantidad_recibida", "fecha_entrega"], "sistema": ["id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]},
            "pdf": ["cantidad_recibida", "fecha_entrega" "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },


        "inventario": {
            "main_page": ["id_producto_nombre", "cantidad"],
            "modal": ["id", "id_producto_nombre", "cantidad", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"],
            "pdf": ["id_producto_nombre", "cantidad", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },
        "ubicaciones": {
            "main_page": ["id_visualizacion", "nombre", "estatus"],
            "modal": ["id", "nombre", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"],
            "pdf": ["nombre", "estatus", "id_usuario_correo_electronico", "fecha_de_creacion", "fecha_de_actualizacion"]
        },
        "cuenta_banco": {
            "main_page": ["id_visualizacion", "nombre", "banco", "saldo_inicial", "saldo_actual", "estatus"],
            "modal": ["id", "id_visualizacion", "nombre", "banco", "tipo_cuenta", "numero_cuenta", "clabe", "saldo_inicial",  "estatus", "fecha_de_creacion"],
            "pdf": ["nombre", "banco", "saldo_actual", "moneda"]
        },
        "gasto": {
            "main_page": ["id_visualizacion", "id_categoria_nombre", "descripcion", "monto", "fecha", "estatus"],
            "modal": ["id", "id_visualizacion", "id_categoria_nombre", "descripcion", "monto", "fecha", "archivo_comprobante", "estatus"],
            "pdf": ["id_visualizacion", "descripcion", "monto", "fecha"]
        },
        "categoria_gasto": {
            "main_page": ["id_visualizacion", "nombre", "descripcion", "estatus"],
            "modal": ["id", "id_visualizacion", "nombre", "descripcion", "estatus", "fecha_de_creacion"],
            "pdf": ["nombre", "descripcion"]
        },
        "pago": {
            "main_page": ["id_visualizacion", "id_gasto_descripcion", "id_cuenta_nombre", "monto", "fecha", "estatus"],
            "modal": ["id", "id_visualizacion", "id_gasto_descripcion", "id_cuenta_nombre", "monto", "fecha", "referencia", "estatus"],
        },

    }
    # Si la tabla no está configurada en "columns", regresa None para que la
    # lógica que llama a esta función pueda usar un fallback genérico.
    table_config = columns.get(table_name)
    if not table_config:
        return None

    # Si la sección (main_page, modal, pdf, etc.) no existe para esa tabla,
    # también regresamos None y dejamos que el caller decida el comportamiento.
    # columns = table_config.get(section)

    columns = columns.get(table_name).get(section)
    return columns


def get_table_buttons():
    buttons = {
        "reportes": 1,
        "inventario": 1
    }
    return buttons


def get_estatus_options(table_name):
    options = {
        'ordenes_de_compra': ["En revisión", "Aprobada", 'Recibida parcial', "Recibida", 'Finalizada', "Cancelada"],
        "productos_en_ordenes_de_compra": ['Pendiente', 'Recibido parcial', 'Recibido'],
        'gasto': ["En revisión", "Aprobado", "Pagado parcial", "Pagado", "Cancelado"],
        'pago': ["En revisión", "Aprobado", "Pagado", "Cancelado"],
        'transferencia_inventario': ["En revisión", "Aprobado", "Realizado"],
        # Sin estatus para existencias (evita tabs de estatus que no aplican)
        'existencias': [],

    }
    options = options.get(table_name, ["Activo", "Inactivo"])
    return options


def get_open_status(table_name):
    status = {
        # "ordenes_de_compra": ['En revisión', 'Aprobada', 'Recibida parcial', 'Recibida'],
        # "productos_en_ordenes_de_compra": ['Pendiente', 'Recibida parcial'],
        "ordenes_de_compra": ['En revisión', 'Aprobada', 'Recibida parcial', 'Recibida'],
        "productos_en_ordenes_de_compra": ['Pendiente', 'Recibida parcial', 'Recibida'],
        "transferencia_inventario": ['En revisión', 'Aprobado'],

    }
    status = status.get(table_name, '')
    return status


def get_breadcrumbs(table_name):
    # [modulo,active_menu]
    breadcrumbs = {
        "usuarios": ['Permisos', 'permisos'],
        "roles": ['Permisos', 'permisos'],
        "logs_auditoria": ['Auditoría', 'auditoria'],
        "reportes": ['Reportes', 'reportes'],
        "categorias_de_reportes": ['Reportes', 'reportes'],
        "archivos": [session['tabla_origen'].replace('_', ' ').capitalize(), session['tabla_origen']],

        "productos": ['Cátalogos', 'catalogos'],
        # "ubicaciones": ['Cátalogos', 'catalogos'],
        "proveedores": ['Cátalogos', 'catalogos'],
        "ordenes_de_compra": ['Compras', 'compras'],
        "productos_en_ordenes_de_compra": ['Compras', 'compras'],
        # "ubicaciones": ['Cátalogos', 'catalogos'],

        # Inventario
        "almacen": ['Inventario', 'inventario'],
        "existencias": ['Inventario', 'inventario'],
        "productos_inventario": ['Inventario', 'inventario'],
        "transferencia_inventario": ['Inventario', 'inventario'],


        # "ordenes_de_compra": ['Compras', 'ordenes_de_compras'],
        # "productos_en_ordenes_de_compra": ['Compras', 'ordenes_de_compras'],
        "entrega_de_productos_en_ordenes_de_compra": ['Compras', 'ordenes_de_compras'],
        "cuenta_banco": ['Finanzas', 'finanzas'],
        "gasto": ['Finanzas', 'finanzas'],
        "pago": ['Finanzas', 'finanzas'],
        "categoria_gasto": ['Finanzas', 'finanzas'],
        "inventario": ['Compras', 'compras']
    }
    breadcrumbs = breadcrumbs.get(
        table_name, ['Bases de datos', 'bases_de_datos'])
    return breadcrumbs[0], breadcrumbs[1]


def get_table_relationships(table_name):
    relationships = {
        "ordenes_de_compra": ["productos_en_ordenes_de_compra"],
        "productos_en_ordenes_de_compra": ["entrega_de_productos_en_ordenes_de_compra"],
    }
    relationships = relationships.get(table_name, [])
    if table_name not in ('archivos', 'usuarios', 'roles', 'logs_auditoria', 'rutas', 'categorias_de_reportes'):
        relationships.append('archivos')
    return relationships


def get_calendar_date_variable(table_name):
    date_variable = {
        "ordenes_de_compra": "fecha_orden"
    }
    date_variable = date_variable.get(table_name, '')
    return date_variable


def get_variable_tabs(table_name):
    tabs = {
        "gasto": "estatus",
        # Para existencias no usamos estatus; agrupamos, por ejemplo, por producto
        "existencias": "id_producto",
    }
    tabs = tabs.get(table_name, 'estatus')
    return tabs


def get_data_tabs(table_name, parent_table, id_parent_record):
    column_tabs = get_variable_tabs(table_name)
    tabs = get_estatus_options(table_name)
    model = get_model_by_name(table_name)
    column = getattr(model, column_tabs, None)
    count_col = func.count().label("count")
    query = db.session.query(column, count_col).group_by(column)
    if parent_table and id_parent_record:
        for rel in model.__mapper__.relationships.values():
            related_table_name = rel.mapper.class_.__tablename__
            if related_table_name == parent_table:
                fk_column = list(rel.local_columns)[0]
                query = query.filter(fk_column == id_parent_record)
                break
    query = query.order_by(count_col.desc())
    results = dict(query.all())
    results = [
        {
            'tab': estatus if estatus else 'Sin estatus',
            'count': results.get(estatus, 0)
        }
        for estatus in tabs
    ]
    return results


def get_date_fields():
    # date_fields = ["fecha_orden", "fecha_gasto", "fecha_pago", "fecha"]
    date_fields = ["fecha_orden"]
    return date_fields


def get_checkbox(table_name):
    checkbox = {
        # 'ordenes_de_compra': True,
        # 'gasto': True
        'table_name': True,
    }
    checkbox = checkbox.get(table_name, False)
    return checkbox


def get_summary_data(table_name):
    data = {
        'table_name': {
            'primary': ["column_name"],
            'data': {"section_name": ["column_name"], "section_name": ["variacolumn_namebles"]}
        },
    }
    data = data.get(table_name, '')
    return data


def get_summary_kpis(table_name, id_parent_record):
    data = {
        "table_name": {
            "section_name": {
                "kp_name": get_kpi(table_name, "sql_name", {"variable": id_parent_record})
            },
        }
    }
    data = data.get(table_name, '')
    return data
