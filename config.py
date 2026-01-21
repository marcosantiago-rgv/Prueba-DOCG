# title format replacements
from python.models import inventario


TITLE_FORMATS = {
    "id_visualizacion": 'ID',
    "creacion": "creación",
    "descripcion": "descripción",
    "informacion": "información",
    "categoria": "categoría",
    "menu": "menú",
    "telefono": "teléfono",
    "razon": "razón",
    "metodo": "método",
    "transito": "tránsito",
    "periodico": "periódico",
    "genero": "género",
    "direccion": "dirección",
    "codigo": "código",
    "contratacion": "contratación",
    "numero": "número",
    "razon": "razón",
    "direccion": "dirección",
    "nomina": "nómina",
    "electronico": "electrónico",
    "ultimo": "último",
    "sesion": "sesión",
    "metodo": "método",
    "comision": "comisión",
    "codigo": "código",
    "actualizacion": "actualización",
    "ejecucion": "ejecución",
    "dias": "días",
    "transito": "tránsito",
    "interaccion": "interacción",
    "interacciones": "interacciones",
    "ultima": 'última',
    "region": 'región',
    "cotizacion": 'cotización',
    "accion": "acción",
    "gasto": "gastos",
    "pago": "pagos",
    "categoria_gasto": "Categorías de Gastos",
    "cuenta_banco": "Cuentas bancarias",
    "id_orden_de_compra_id_visualizacion": "ID Compra",
    "id_proveedor_nombre": "ID Proveedor",
    "almacen": "almacén",
    "existencias": "Existencias En Stock De Inventario",
}

# column names for data imports
TABLE_COLUMN_MAPS = {
    "ordenes_de_compra": {
        "Fecha entrega": 'fecha_de_entrega',
    }
}
