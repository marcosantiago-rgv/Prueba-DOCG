SELECT 
  poeoc.id AS id,
  poeoc.id_producto,
  p.nombre,
  poeoc.cantidad_recibida - COALESCE(SUM(dti.cantidad), 0) AS cantidad,
  p.unidad_de_medida,
  poeoc.fecha_entrega_estimada AS fecha_de_creacion
FROM productos_en_ordenes_de_compra poeoc
JOIN productos p ON poeoc.id_producto = p.id
LEFT JOIN detalle_transferencia_inventario dti
  ON dti.id_producto = poeoc.id_producto
WHERE p.estatus = 'Activo'
  AND poeoc.estatus = 'Recibido'
  AND poeoc.cantidad_recibida > 0
GROUP BY poeoc.id, poeoc.id_producto, p.nombre, poeoc.cantidad_recibida, p.unidad_de_medida, poeoc.fecha_entrega_estimada
HAVING (poeoc.cantidad_recibida - COALESCE(SUM(dti.cantidad), 0)) > 0
