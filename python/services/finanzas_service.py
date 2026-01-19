from python.models.modelos import MovimientoBancario 
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