SELECT
    TO_CHAR(fecha, 'YYYY-MM') AS mes,
    SUM(monto) AS total_pagado
FROM movimiento_bancario
WHERE tipo = 'Egreso'
GROUP BY TO_CHAR(fecha, 'YYYY-MM')
ORDER BY mes;
