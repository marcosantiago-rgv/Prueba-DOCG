SELECT
    dti.id,
    dti.id_transferencia,
    dti.id_producto,
    p.nombre AS nombre,
    dti.cantidad,
    p.unidad_de_medida AS unidad_de_medida,
    dti.fecha_de_creacion
FROM detalle_transferencia_inventario dti
JOIN productos p ON p.id = dti.id_producto
WHERE dti.id_transferencia = :id_main_record
ORDER BY dti.fecha_de_creacion DESC
