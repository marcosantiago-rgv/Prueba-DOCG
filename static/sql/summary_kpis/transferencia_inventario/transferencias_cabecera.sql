SELECT
  ti.id,
  ti.id_visualizacion,
  ti.fecha,
  ti.estatus,
  ao.nombre AS almacen_origen,
  ad.nombre AS almacen_destino
FROM transferencia_inventario ti
JOIN almacen ao ON ti.id_almacen_origen = ao.id
JOIN almacen ad ON ti.id_almacen_destino = ad.id
ORDER BY ti.fecha DESC;