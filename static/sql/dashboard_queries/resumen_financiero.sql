WITH t_gastos AS (
    SELECT COALESCE(SUM(monto), 0) as suma 
    FROM gasto 
    WHERE fecha >= :fecha_inicio AND fecha <= :fecha_fin AND estatus != 'Cancelado'
),
t_pagos AS (
    SELECT COALESCE(SUM(monto), 0) as suma 
    FROM movimiento_bancario 
    WHERE fecha >= :fecha_inicio AND fecha <= :fecha_fin AND tipo = 'Egreso'
)
SELECT 
    t_gastos.suma as total_gastos, 
    t_pagos.suma as total_pagos, 
    5 as tendencia 
FROM t_gastos, t_pagos;