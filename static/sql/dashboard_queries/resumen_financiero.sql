WITH t_gastos AS (
  SELECT
    COALESCE(SUM(monto), 0) as suma
  FROM
    gasto
  WHERE
    fecha >= :fecha_inicio
    AND fecha <= :fecha_fin
    -- Quitamos 'Pendiente' si solo quieres ver lo que ya está validado,
    -- o lo dejamos si quieres ver deuda proyectada.
    AND estatus IN ('Aprobado', 'Pagado', 'Pagado parcial', 'Pendiente')
)
, t_pagos AS (
  SELECT
    COALESCE(SUM(pg.monto_aplicado), 0) as suma
  FROM
    pagos_gastos pg
    JOIN gasto g
  ON pg.id_gasto = g.id
  WHERE
    g.fecha >= :fecha_inicio
    AND g.fecha <= :fecha_fin
    -- Eliminamos el JOIN con 'pago p' y su estatus para que cuente
    -- el dinero en cuanto se aplica, no hasta que se aprueba el pago.
)
SELECT
  t_gastos.suma as total_gastos
  , t_pagos.suma as total_pagos
  , (t_gastos.suma - t_pagos.suma) as saldo_pendiente
  , 5 as tendencia
FROM
  t_gastos
  , t_pagos;