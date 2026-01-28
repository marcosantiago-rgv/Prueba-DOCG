SELECT
  COUNT(id) as indicador
FROM
  ordenes_de_compra
WHERE
  id_proveedor = :id_proveedor
  AND estatus IN ('En revisión', 'Aprobada')