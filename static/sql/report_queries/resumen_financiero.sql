SELECT 'Total Gastos' as concepto, COALESCE(SUM(monto), 0) as importe
FROM gasto
WHERE estatus != 'Cancelado'
UNION ALL
SELECT 'Total Pagado' as concepto, COALESCE(SUM(monto), 0) as importe
FROM movimiento_bancario
WHERE tipo = 'Egreso'