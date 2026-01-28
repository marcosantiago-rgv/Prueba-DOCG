SELECT
  COUNT(id) as indicador
FROM
  ordenes_de_compra
WHERE
  id_proveedor = :id_proveedor
  AND fecha_entrega_real <= fecha_entrega_estimada