WITH t_gastos AS (
    SELECT COALESCE(SUM(monto), 0) as suma 
    FROM gasto 
    WHERE fecha >= :fecha_inicio AND fecha <= :fecha_fin 
    AND estatus IN ('Aprobado', 'Pagado', 'Pendiente') 
),
t_pagos AS (
    SELECT COALESCE(SUM(p.monto), 0) as suma 
    FROM pago p
    JOIN gasto g ON p.id_gasto = g.id
    WHERE g.fecha >= :fecha_inicio AND g.fecha <= :fecha_fin 
    AND p.estatus = 'Pagado' 
)
SELECT 
    t_gastos.suma as total_gastos, 
    t_pagos.suma as total_pagos,
    (t_gastos.suma - t_pagos.suma) as saldo_pendiente,
    5 as tendencia 
FROM t_gastos, t_pagos;