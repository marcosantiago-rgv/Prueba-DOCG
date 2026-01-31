SELECT 
    c.nombre AS categoria, 
    SUM(g.monto) AS total 
FROM gasto g
JOIN categoria_gasto c ON g.id_categoria = c.id
WHERE g.estatus != 'Cancelado'
GROUP BY c.nombre
ORDER BY total DESC;