SELECT
  COALESCE(SUM(monto), 0) as indicador
FROM
  gasto
WHERE
  id_proveedor = :id_proveedor
  AND estatus != 'Cancelado'