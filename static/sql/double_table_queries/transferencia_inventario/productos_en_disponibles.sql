-- Productos disponibles para transferencia, incluyendo:
-- 1. Existencias físicas en almacén
-- 2. Productos en órdenes de compra pendientes o recibidos parcialmente

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

UNION

SELECT 
  poeoc.id AS id,
  poeoc.id_producto,
  p.nombre,
  (poeoc.cantidad_ordenada - COALESCE(poeoc.cantidad_recibida,0)) AS cantidad,
  p.unidad_de_medida,
  poeoc.fecha_entrega_estimada AS fecha_de_creacion
FROM productos_en_ordenes_de_compra poeoc
JOIN productos p ON poeoc.id_producto = p.id
WHERE p.estatus = 'Activo'
  AND (poeoc.estatus = 'Pendiente' OR poeoc.estatus = 'Recibido parcial')
  AND (poeoc.cantidad_ordenada - COALESCE(poeoc.cantidad_recibida,0)) > 0
  AND NOT EXISTS (
    SELECT 1
    FROM detalle_transferencia_inventario dti
    WHERE dti.id_transferencia = :id_main_record
      AND dti.id_producto = poeoc.id_producto
  )
-- Puedes agregar más filtros según almacén, usuario, etc.
