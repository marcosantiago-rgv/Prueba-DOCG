SELECT
  pg.id
  , g.id_visualizacion
  , g.descripcion
  , pg.monto_aplicado
  , pg.fecha_de_creacion
FROM
  pagos_gastos pg
  JOIN gasto g
ON pg.id_gasto = g.id
WHERE
  pg.id_pago = :id_main_record