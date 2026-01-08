select
    TO_CHAR(fecha_orden,'YYYY-MM-DD') as fecha,
    sum(importe_total) as importe_total
from ordenes_de_compra
group by 
    TO_CHAR(fecha_orden,'YYYY-MM-DD')
