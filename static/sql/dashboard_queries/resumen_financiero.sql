WITH t_gastos AS (
  SELECT
    COALESCE(SUM(monto), 0) as suma
  FROM
    gasto
  WHERE
    fecha >= :fecha_inicio
    AND fecha <= :fecha_fin
    AND estatus IN ('Aprobado', 'Pagado', 'Pagado parcial')
)
, t_pagos AS (
  SELECT
    COALESCE(SUM(pg.monto_aplicado), 0) as suma
  FROM
    pagos_gastos pg
    JOIN gasto g
  ON pg.id_gasto = g.id
  JOIN pago p
  ON pg.id_pago = p.id
  WHERE
    g.fecha >= :fecha_inicio
    AND g.fecha <= :fecha_fin
    AND p.estatus = 'Pagado'
)
SELECT
  t_gastos.suma as total_gastos
  , t_pagos.suma as total_pagos
  , (t_gastos.suma - t_pagos.suma) as saldo_pendiente
  , 5 as tendencia
FROM
  t_gastos
  , t_pagos;