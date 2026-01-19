/*
Consulta de transferencias de inventario filtro mes actual.

- Selecciona de la tabla "transferencia_inventario" las columnas: 
  "fecha", "cantidad" y "estatus".
- Selecciona de la tabla "productos" el "nombre" del producto.
- Selecciona de la tabla "almacen" los nombres del almacén de origen y del almacén destino.
- Une las tablas usando los IDs correctos: 
  "id_producto", "id_almacen_origen", "id_almacen_destino".
- Filtra solo las transferencias cuya fecha esté dentro del mes actual.
- Ordena los resultados por fecha descendente y luego por nombre del producto.
*/
SELECT
    transferencia_inventario.fecha,
    producto.nombre AS producto,
    almacen_origen.nombre AS almacen_origen,
    almacen_destino.nombre AS almacen_destino,
    transferencia_inventario.cantidad,
    transferencia_inventario.estatus
FROM transferencia_inventario transferencia_inventario
JOIN productos producto ON producto.id = transferencia_inventario.id_producto
JOIN almacen almacen_origen ON almacen_origen.id = transferencia_inventario.id_almacen_origen
JOIN almacen almacen_destino ON almacen_destino.id = transferencia_inventario.id_almacen_destino
WHERE transferencia_inventario.fecha >= date_trunc('month', current_date)
  AND transferencia_inventario.fecha < (date_trunc('month', current_date) + interval '1 month')
ORDER BY transferencia_inventario.fecha DESC, producto.nombre
