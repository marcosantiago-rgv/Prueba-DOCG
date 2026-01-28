SELECT
    cb.nombre AS cuenta,
    SUM(mb.monto) AS total_egresos
FROM movimiento_bancario mb
JOIN cuenta_banco cb ON cb.id = mb.id_cuenta
WHERE mb.tipo = 'Egreso'
GROUP BY cb.nombre