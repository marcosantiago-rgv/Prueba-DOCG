/*
Reporte de movimientos de inventario del mes actual por producto.

- Selecciona de la tabla productos EL
    - "nombre" del producto.
- Selecciona de la tabla "transferencia_inventario":
    - La fecha mínima de movimiento ("MIN(ti.fecha)") para saber cuándo se registró la primera transferencia del mes.
    - La cantidad total de entradas ("SUM(...) AS entradas"): suma de todas las transferencias hacia un almacén en el mes.
    - La cantidad total de salidas ("SUM(...) AS salidas"): suma de todas las transferencias desde un almacén en el mes.
- Filtra solo las transferencias del mes actual usando `date_trunc('month', current_date)".
- Agrupa los resultados por producto para obtener un resumen por producto.
- Ordena los resultados alfabéticamente por el nombre del producto.
*/
SELECT
    p.nombre AS producto,
    MIN(ti.fecha) AS fecha,
    SUM(CASE WHEN ti.id_almacen_destino IS NOT NULL THEN ti.cantidad ELSE 0 END) AS entradas,
    SUM(CASE WHEN ti.id_almacen_origen IS NOT NULL THEN ti.cantidad ELSE 0 END) AS salidas
FROM transferencia_inventario ti
JOIN productos p ON p.id = ti.id_producto
WHERE ti.fecha >= date_trunc('month', current_date)
  AND ti.fecha < (date_trunc('month', current_date) + interval '1 month')
GROUP BY p.nombre
ORDER BY p.nombre