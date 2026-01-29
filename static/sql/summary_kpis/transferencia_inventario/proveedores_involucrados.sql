SELECT DISTINCT
  pr.nombre,
  pr.razon_social,
  pr.email
FROM proveedores pr
JOIN ordenes_de_compra oc ON oc.id_proveedor = pr.id
JOIN productos_en_ordenes_de_compra poc ON poc.id_orden_de_compra = oc.id
JOIN detalle_transferencia_inventario dti ON dti.id_producto = poc.id_producto
WHERE dti.id_transferencia = :id_transferencia;