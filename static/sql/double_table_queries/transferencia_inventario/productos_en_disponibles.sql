-- Productos disponibles para transferencia, filtrando los que ya están en la transferencia actual
SELECT 
  e.id AS id,
  e.id_producto,
  p.nombre,
  e.cantidad,
  p.unidad_de_medida,
  e.fecha_de_creacion
FROM existencia e
JOIN productos p ON e.id_producto = p.id
WHERE p.estatus = 'Activo'
  AND e.cantidad > 0
  AND NOT EXISTS (
    SELECT 1
    FROM detalle_transferencia_inventario dti
    WHERE dti.id_transferencia = :id_main_record
      AND dti.id_producto = e.id_producto
  )
-- Puedes agregar más filtros según almacén, usuario, etc.
