from datetime import timedelta
from python.services.system.helper_functions import *
from python.models.modelos import *
from sqlalchemy import or_, and_, func
from python.services.finanzas_service import FinanzasService
###############
#  Duuble Table View
###################


def get_variables_double_table_view(table_name):
    columns = {
        "ordenes_de_compra": {
            "columns_first_table": ["nombre"],
            "columns_second_table": ["nombre", "cantidad_ordenada", "precio_unitario", "subtotal", "descuento_porcentaje", "importe_total", "fecha_entrega_estimada", "archivo_cotizacion"],
            "title_first_table": "Productos",
            "title_second_table": "Productos en orden de compra",
            "query_first_table": "productos",
            "query_second_table": "productos_en_orden_de_compra",
            "model_first_table": "productos",
            "model_second_table": "productos_en_ordenes_de_compra",
            "edit_fields": ['precio_unitario', 'cantidad_ordenada', 'descuento_porcentaje', 'subtotal', 'fecha_entrega_estimada'],
            "required_fields": ['precio_unitario', 'cantidad_ordenada', 'descuento_porcentaje', 'subtotal', 'fecha_entrega_estimada'],
            "details": ["id_visualizacion", "proveedor.nombre", 'importe_total'],
            "url_confirm": "ordenes_de_compra.confirmar"
        },
        "pago": {
            "columns_first_table": ["id_visualizacion", "descripcion", "monto"],
            "columns_second_table": ["id_visualizacion", "descripcion", "monto_aplicado"],
            "title_first_table": "Gastos Disponibles",
            "title_second_table": "Gastos asociados al Pago",
            "query_first_table": "gastos_disponibles",
            "query_second_table": "gastos_seleccionados",
            "model_first_table": "gasto",
            "model_second_table": "pagos_gastos",
            "edit_fields": ['monto_aplicado'],
            "required_fields": ['monto_aplicado'],
            "details": ["id_visualizacion", "cuenta.nombre", "monto", "referencia"],
            "url_confirm": "pago.aprobar"
        },
        "transferencia_inventario": {
            "columns_first_table": ["nombre", "cantidad", "unidad_de_medida"],
            "columns_second_table": ["nombre", "cantidad", "unidad_de_medida", "fecha_de_creacion"],
            "title_first_table": "Productos en almacén origen",
            "title_second_table": "Productos a transferir",
            "query_first_table": "productos_en_disponibles",
            "query_second_table": "detalle_transferencia_inventario",
            "model_first_table": "existencia",
            "model_second_table": "detalle_transferencia_inventario",
            "edit_fields": ["cantidad"],
            "required_fields": ["cantidad"],
            "details": ["id_visualizacion", "almacen_origen.nombre", "almacen_destino.nombre", "fecha", "estatus"],
            "url_confirm": "transferencia_inventario.confirmar",
            "default_sort_field": "fecha_de_creacion"
        }

    }
    columns = columns.get(table_name, '')
    return columns


def add_record_double_table(main_table_name, second_table, id_main_record, id_record):
    model = get_model_by_name(second_table)
    from python.models import db
    if main_table_name == 'ordenes_de_compra':
        orden = OrdenesDeCompra.query.get(id_main_record)
        # Validar si ya existe el producto en la orden
        existe = model.query.filter_by(
            id_orden_de_compra=id_main_record, id_producto=id_record).first()
        if existe:
            return existe  # Ya existe, no crear duplicado
        if not orden:
            raise Exception('Orden de compra no encontrada')
        new_record = model(
            id_orden_de_compra=id_main_record,
            id_producto=id_record,
            precio_unitario=0,
            cantidad_ordenada=0,
            cantidad_recibida=0,
            descuento_porcentaje=0,
            subtotal=0,
            fecha_entrega_estimada=orden.fecha_entrega_estimada,
            id_usuario=session['id_usuario']
        )
        return new_record
    elif main_table_name == 'pago':
        gasto_original = Gasto.query.get(id_record)
        if not gasto_original:
            raise Exception('Gasto no encontrado')
        
        total_pagado_previo = db.session.query(func.sum(PagosGastos.monto_aplicado)).filter(
            PagosGastos.id_gasto == id_record
        ).scalar() or 0
        
        saldo_pendiente = gasto_original.monto - total_pagado_previo
        
        if saldo_pendiente <= 0:
            raise Exception('Este gasto ya ha sido liquidado en su totalidad')

        new_record = model(
            id_pago=id_main_record,
            id_gasto=id_record,
            monto_aplicado=saldo_pendiente,
            id_usuario=session['id_usuario']
        )
        
        db.session.add(new_record)
        db.session.flush() 

        FinanzasService.recalcular_total_pago(id_main_record)
        FinanzasService.actualizar_estatus_gasto(id_record) 
        
        db.session.commit() 
        return new_record
    elif main_table_name == 'transferencia_inventario':
        existencia = Existencia.query.get(id_record)
        if not existencia:
            raise Exception('Existencia no encontrada')
        # Inicializar la cantidad con la cantidad disponible en el almacén origen
        cantidad_disponible = existencia.cantidad if existencia.cantidad is not None else 0
        new_record = model(
            id_transferencia=id_main_record,
            id_producto=existencia.id_producto,
            cantidad=cantidad_disponible,
            id_usuario=session['id_usuario']
        )
        db.session.add(new_record)
        db.session.commit()
        return new_record
    else:
        raise Exception('Tipo de tabla no soportado')


def validate_delete(table_name, id):
    if table_name == 'table_name':
        record = table_name.query.get(id)
        if record.column == '':
            return False
    return True


def on_add_double_table(table_name, id):
    if table_name == 'ejemplo':
        orden = OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)


def on_update_double_table(table_name, id):
    if table_name == 'ejemplo':
        orden = OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)


def on_delete_double_table(table_name, id):
    if table_name == 'ejemplo':
        orden = OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)
