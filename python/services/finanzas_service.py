from python.models.modelos import MovimientoBancario, Pago, PagosGastos, Gasto
from python.models import db
from sqlalchemy import func

class FinanzasService:
    @staticmethod
    def obtener_saldo_calculado(id_cuenta, saldo_inicial):
        """
        Calcula el saldo proyectado sumando ingresos y restando egresos
        al saldo inicial de la cuenta.
        """
        # Sumar todos los movimientos de tipo 'Ingreso'
        ingresos = db.session.query(func.sum(MovimientoBancario.monto)).filter(
            MovimientoBancario.id_cuenta == id_cuenta,
            MovimientoBancario.tipo == 'Ingreso'
        ).scalar() or 0

        # Sumar todos los movimientos de tipo 'Egreso'
        egresos = db.session.query(func.sum(MovimientoBancario.monto)).filter(
            MovimientoBancario.id_cuenta == id_cuenta,
            MovimientoBancario.tipo == 'Egreso'
        ).scalar() or 0

        # Retornar el cálculo final 
        return (saldo_inicial or 0) + ingresos - egresos
    @staticmethod
    def recalcular_total_pago(pago_id):
        """Suma los montos de la tabla intermedia y asegura el estatus de revisión"""
        db.session.flush() 
        
        # Solo sumamos montos de pagos que no estén cancelados
        total = db.session.query(func.sum(PagosGastos.monto_aplicado)).filter(
            PagosGastos.id_pago == pago_id
        ).scalar() or 0
        
        pago = Pago.query.get(pago_id)
        if pago:
            pago.monto = total
            
            if pago.estatus not in ['Pagado', 'Cancelado']:
                pago.estatus = 'En revisión'
                
            db.session.add(pago) 
        return total
    @staticmethod
    def actualizar_estatus_gasto(id_gasto):
        db.session.flush() 
        
        gasto = Gasto.query.get(id_gasto)
        if not gasto:
            return

        total_pagado = db.session.query(func.sum(PagosGastos.monto_aplicado))\
            .join(Pago, PagosGastos.id_pago == Pago.id)\
            .filter(
                PagosGastos.id_gasto == id_gasto,
                Pago.estatus != 'Cancelado' 
            ).scalar() or 0

        if total_pagado <= 0:
            gasto.estatus = 'Aprobado' 
        elif total_pagado < gasto.monto:
            gasto.estatus = 'Pagado parcial'
        else:
            gasto.estatus = 'Pagado'
            
        db.session.add(gasto)