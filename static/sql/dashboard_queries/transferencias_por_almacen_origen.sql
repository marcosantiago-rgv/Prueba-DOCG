-- transferencias_por_almacen_origen.sql
-- Devuelve el total transferido por almacén origen para dashboard
SELECT
  a.nombre AS almacen_origen,
  SUM(dti.cantidad) AS total_transferido
FROM transferencia_inventario ti
JOIN detalle_transferencia_inventario dti
  ON ti.id = dti.id_transferencia
JOIN almacen a ON ti.id_almacen_origen = a.id
GROUP BY a.nombre
ORDER BY total_transferido DESC;