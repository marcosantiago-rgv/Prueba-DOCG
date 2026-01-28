SELECT DISTINCT
  oc.id_visualizacion AS orden,
  oc.fecha_orden,
  oc.estatus,
  p.nombre AS producto,
  poc.cantidad_ordenada,
  poc.precio_unitario
FROM ordenes_de_compra oc
JOIN productos_en_ordenes_de_compra poc
  ON poc.id_orden_de_compra = oc.id
JOIN productos p
  ON poc.id_producto = p.id
JOIN detalle_transferencia_inventario dti
  ON dti.id_producto = p.id
WHERE dti.id_transferencia = :id_transferencia
ORDER BY oc.fecha_orden DESC;