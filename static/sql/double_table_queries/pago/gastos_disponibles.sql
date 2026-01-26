SELECT
  id
  , id_visualizacion
  , descripcion
  , monto
  , fecha_de_creacion
FROM
  gasto
WHERE
  estatus IN ('Aprobado', 'Pagado parcial')
  AND NOT EXISTS (
    SELECT
      1
    FROM
      pagos_gastos pg
    WHERE
      pg.id_gasto = gasto.id
      AND pg.id_pago = :id_main_record
  )