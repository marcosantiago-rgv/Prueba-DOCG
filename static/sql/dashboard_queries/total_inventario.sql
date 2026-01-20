SELECT
    (SELECT COUNT(*)
     FROM productos
     WHERE estatus = 'Activo') AS total_productos,

    (SELECT COUNT(*)
     FROM almacen
     WHERE estatus = 'Activo') AS total_almacenes,

    (SELECT COUNT(*)
     FROM transferencia_inventario
     WHERE fecha >= date_trunc('month', current_date)
       AND fecha < (date_trunc('month', current_date) + interval '1 month')
    ) AS total_transferencias
