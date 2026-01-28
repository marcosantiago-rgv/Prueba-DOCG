import uuid 
from flask import Blueprint, flash, redirect, url_for, request, session
from python.models import db
from python.models.modelos import Gasto, Pago, CuentaBanco, MovimientoBancario, PagosGastos
from datetime import datetime
from sqlalchemy import func
from python.services.finanzas_service import FinanzasService

gasto_bp = Blueprint('gasto', __name__, url_prefix='/gasto')

@gasto_bp.route('/aprobar/<id>', methods=['GET', 'POST'])
def aprobar(id):
    try:
        record = Gasto.query.get(id)
        if record and record.estatus == 'En revisión':
            record.estatus = "Aprobado"
            db.session.commit()
            flash('Gasto aprobado correctamente.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('dynamic.table_view', table_name='gasto'))


def generar_id_visual(modelo):
    """Función interna para evitar errores de importación"""
    max_id = db.session.query(func.max(modelo.id_visualizacion)).scalar()
    return (max_id or 0) + 1

@gasto_bp.route('/pagar_rapido/<id>')
def pagar_rapido(id):
    try:
        gasto_obj = Gasto.query.get(uuid.UUID(id) if isinstance(id, str) else id)
        cuenta_obj = CuentaBanco.query.filter_by(estatus='Activo').first()
        
        if not gasto_obj or not cuenta_obj:
            flash('Gasto o Cuenta no encontrados', 'danger')
            return redirect(url_for('dynamic.table_view', table_name='gasto'))

        nuevo_pago = Pago(
            id_cuenta=cuenta_obj.id,
            monto=gasto_obj.monto,
            fecha=datetime.utcnow().date(),
            estatus="Pagado",
            id_visualizacion=generar_id_visual(Pago),
            id_usuario=session.get('id_usuario')
        )
        db.session.add(nuevo_pago)
        db.session.flush()

        nueva_relacion = PagosGastos(
            id_pago=nuevo_pago.id,
            id_gasto=gasto_obj.id,
            monto_aplicado=gasto_obj.monto
        )
        db.session.add(nueva_relacion)
        
        gasto_obj.estatus = "Pagado"
        
        nuevo_movimiento = MovimientoBancario(
            id_cuenta=cuenta_obj.id,
            tipo='Egreso',
            monto=gasto_obj.monto,
            descripcion=f"Pago Rápido Gasto #{gasto_obj.id_visualizacion}",
            fecha=datetime.utcnow().date(),
            id_visualizacion=generar_id_visual(MovimientoBancario),
            id_usuario=session.get('id_usuario')
        )
        db.session.add(nuevo_movimiento)
        
        db.session.flush() 
        cuenta_obj.saldo_actual = FinanzasService.obtener_saldo_calculado(
            cuenta_obj.id, 
            cuenta_obj.saldo_inicial
        )
        
        db.session.commit()
        flash('Pago procesado correctamente', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        
    return redirect(url_for('dynamic.table_view', table_name='gasto'))

@gasto_bp.route('/ir_a_pagos/<id>')
def ir_a_pagos(id):
    return redirect(url_for('dynamic.table_view', table_name='pago'))


@gasto_bp.route('/cancelar/<id>', methods=['GET', 'POST'])
def cancelar(id):
    """
    Cancela el gasto 
    """
    try:
        gasto_id = uuid.UUID(id) if isinstance(id, str) else id
        gasto_obj = Gasto.query.get(gasto_id)
        
        if gasto_obj:
          
            gasto_obj.estatus = "Cancelado"

        
            pago_asociado = Pago.query.filter_by(id_gasto=gasto_obj.id).first()
            if pago_asociado and pago_asociado.estatus != 'Pagado':
                pago_asociado.estatus = "Cancelado"
            
            db.session.commit()
            flash('Gasto cancelado correctamente')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar gasto: {str(e)}', 'danger')
        
    return redirect(url_for('dynamic.table_view', table_name='gasto'))