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
            "columns_first_table":["nombre"],
            "columns_second_table":["nombre","cantidad_ordenada","precio_unitario","subtotal","descuento_porcentaje","importe_total","fecha_entrega_estimada","archivo_cotizacion"],
            "title_first_table":"Productos",
            "title_second_table":"Productos en orden de compra",
            "query_first_table":"productos",
            "query_second_table":"productos_en_orden_de_compra",
            "model_first_table":"productos",
            "model_second_table":"productos_en_ordenes_de_compra",
            "edit_fields":['precio_unitario','cantidad_ordenada','descuento_porcentaje','subtotal','fecha_entrega_estimada'],
            "required_fields":['precio_unitario','cantidad_ordenada','descuento_porcentaje','subtotal','fecha_entrega_estimada'],
            "details":["id_visualizacion","proveedor.nombre",'importe_total'],
            "url_confirm":"ordenes_de_compra.confirmar"            
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
    }
    columns=columns.get(table_name,'')
    return columns

def add_record_double_table(main_table_name,second_table,id_main_record,id_record):
    model=get_model_by_name(second_table)
    if main_table_name=='ordenes_de_compra':
        orden=OrdenesDeCompra.query.get(id_main_record)
        new_record=model(
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
    elif main_table_name == 'pago':
        gasto_original = Gasto.query.get(id_record)
        new_record = model(
            id_pago=id_main_record,
            id_gasto=id_record,
            monto_aplicado=gasto_original.monto,
            id_usuario=session['id_usuario']
        )
    return new_record

def validate_delete(table_name,id):
    if table_name=='table_name':
        record=table_name.query.get(id)
        if record.column=='':
            return False
    return True

def on_add_double_table(table_name,id):
    if table_name=='ejemplo':
        orden=OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)

def on_update_double_table(table_name,id):
    if table_name=='ejemplo':
        orden=OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)

def on_delete_double_table(table_name,id):
    if table_name=='ejemplo':
        orden=OrdenesDeVenta.query.get(id)
    if table_name == 'pago':
        FinanzasService.recalcular_total_pago(id)