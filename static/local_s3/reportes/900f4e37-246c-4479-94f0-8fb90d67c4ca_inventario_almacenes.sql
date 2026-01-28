/*
Consulta de almacenes que estan activos.

- Seleccionamos  de la tabla "almacen":
    - "nombre" del almacén
    - "ubicacion"
    - "descripcion"
- le dices filtra solo los almacenes que tengan "estatus = 'Activo'".
- Ordena los resultados alfabéticamente por nombre del almacén.
  TO_CHAR(a.fecha_de_creacion, 'DD/MM/YYYY') AS fecha formatea la fecha de creación del almacén en el formato día/mes/año.
*/

SELECT
    a.nombre AS almacen,
    a.ubicacion,
    a.descripcion,
    TO_CHAR(a.fecha_de_creacion, 'DD/MM/YYYY') AS fecha
FROM almacen a
WHERE a.estatus = 'Activo'
ORDER BY a.nombre