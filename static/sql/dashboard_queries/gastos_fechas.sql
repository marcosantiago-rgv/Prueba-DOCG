SELECT
    TO_CHAR(fecha, 'YYYY-MM-DD') AS fecha,
    SUM(monto) AS total_gastos
FROM gasto
WHERE estatus != 'Cancelado'
GROUP BY fecha
ORDER BY fecha