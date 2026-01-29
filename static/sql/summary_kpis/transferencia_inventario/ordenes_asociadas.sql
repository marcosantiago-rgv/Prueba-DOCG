-- ordenes_asociadas.sql
-- Devuelve la cantidad de órdenes de compra asociadas a la transferencia
SELECT COUNT(DISTINCT poc.id_orden_de_compra) AS ordenes_asociadas
FROM detalle_transferencia_inventario dti
JOIN productos_en_ordenes_de_compra poc
	ON poc.id_producto = dti.id_producto
JOIN transferencia_inventario ti
	ON ti.id = dti.id_transferencia
JOIN ordenes_de_compra oc
	ON oc.id = poc.id_orden_de_compra
WHERE dti.id_transferencia = :id_transferencia
	AND oc.id_almacen = ti.id_almacen_destino;