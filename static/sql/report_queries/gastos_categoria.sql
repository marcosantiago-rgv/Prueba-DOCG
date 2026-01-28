SELECT
    cg.nombre AS categoria,
    SUM(g.monto) AS total
FROM gasto g
JOIN categoria_gasto cg ON cg.id = g.id_categoria
WHERE g.estatus != 'Cancelado'
GROUP BY cg.nombre
ORDER BY total DESC