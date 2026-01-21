/* Consulta de existencia de productos en almacenes.

- Selecciona de la tabla "productos":
    - "nombre" del producto
    - "unidad_de_medida"
- Selecciona de la tabla "almacen":
    - "nombre" del almacén
    - "ubicacion"
- Selecciona de la tabla "existencia":
    - "cantidad" disponible
- Une las tablas usando los IDs correspondientes:
    - "e.id_producto = p.id"
    - "e.id_almacen = a.id"
- Filtra solo los productos y almacenes que estén activos ("estatus = 'Activo'").
- Ordenamos los resultados primero por nombre del producto y luego por nombre del almacén.
*/
SELECT
    p.nombre AS producto,
    p.unidad_de_medida,
    a.nombre AS almacen,
    a.ubicacion,
    e.cantidad
FROM existencia e
JOIN productos p ON p.id = e.id_producto
JOIN almacen a ON a.id = e.id_almacen
WHERE p.estatus = 'Activo'
  AND a.estatus = 'Activo'
ORDER BY p.nombre, a.nombre
