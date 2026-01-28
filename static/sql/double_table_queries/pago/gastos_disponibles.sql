SELECT
    g.id
    , g.id_visualizacion
    , g.descripcion
    , (g.monto - COALESCE((
        SELECT SUM(pg_sub.monto_aplicado)
        FROM pagos_gastos pg_sub
        WHERE pg_sub.id_gasto = g.id
    ), 0)) AS monto
    , g.fecha_de_creacion
FROM
    gasto g
WHERE
    g.estatus IN ('Aprobado', 'Pagado parcial')
    AND NOT EXISTS (
        SELECT 1
        FROM pagos_gastos pg
        WHERE pg.id_gasto = g.id
        AND pg.id_pago = :id_main_record
    )