-- total_cantidad_transferida.sql
-- Devuelve la suma total de cantidad transferida en la transferencia
SELECT COALESCE(SUM(dt.cantidad), 0) AS total_cantidad_transferida
FROM detalle_transferencia_inventario dt
WHERE dt.id_transferencia = :id_transferencia;