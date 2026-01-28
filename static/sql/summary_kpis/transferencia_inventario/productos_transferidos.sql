SELECT
	ti.id_visualizacion AS transferencia,
	p.nombre AS producto,
	p.unidad_de_medida,
	dti.cantidad,
	dti.fecha_de_creacion
FROM detalle_transferencia_inventario dti
JOIN transferencia_inventario ti ON dti.id_transferencia = ti.id
JOIN productos p ON dti.id_producto = p.id
WHERE ti.id = :id_transferencia;
