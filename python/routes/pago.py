import uuid 
from flask import Blueprint, flash, redirect, url_for, request, session
from python.models import db
from python.models.modelos import Gasto, Pago, CuentaBanco, MovimientoBancario
from datetime import datetime
from sqlalchemy import func
from python.services.finanzas_service import FinanzasService

pago_bp = Blueprint('pago', __name__, url_prefix='/pago')

def generar_id_visual(modelo):
    """Función interna para evitar errores de importación"""
    max_id = db.session.query(func.max(modelo.id_visualizacion)).scalar()
    return (max_id or 0) + 1

@pago_bp.route('/aprobar/<id>', methods=['GET', 'POST'])
def aprobar(id):
    try:
        pago_obj = Pago.query.get(uuid.UUID(id) if isinstance(id, str) else id)
        if pago_obj and pago_obj.estatus == 'En revisión':
            pago_obj.estatus = "Aprobado" 
            db.session.commit()
            flash('Pago aprobado')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('dynamic.table_view', table_name='pago'))

@pago_bp.route('/confirmar_pago/<id>', methods=['GET', 'POST'])
def confirmar_pago(id):
    try:
        pago_id = uuid.UUID(id) if isinstance(id, str) else id
        pago_obj = Pago.query.get(pago_id)
        
        if not pago_obj:
            flash('Error: Pago no encontrado', 'danger')
            return redirect(url_for('dynamic.table_view', table_name='pago'))

        if pago_obj.estatus == 'Aprobado':
            pago_obj.estatus = "Pagado"
            
            for detalle in pago_obj.detalles_gastos:
                if detalle.gasto:
                    FinanzasService.actualizar_estatus_gasto(detalle.gasto.id)

            nuevo_movimiento = MovimientoBancario(
                id_cuenta=pago_obj.id_cuenta,
                tipo='Egreso',
                monto=pago_obj.monto,
                descripcion=f"Liquidación Pago #{pago_obj.id_visualizacion} (Múltiples Gastos)",
                fecha=datetime.utcnow().date(),
                id_visualizacion=generar_id_visual(MovimientoBancario),
                id_usuario=session.get('id_usuario')
            )
            db.session.add(nuevo_movimiento)
            
            db.session.flush() 
            cuenta_obj = CuentaBanco.query.get(pago_obj.id_cuenta)
            if cuenta_obj:
                cuenta_obj.saldo_actual = FinanzasService.obtener_saldo_calculado(
                    cuenta_obj.id, cuenta_obj.saldo_inicial
                )
            
            db.session.commit()
            flash('Pago realizado éxito', 'success')
        
        elif pago_obj.estatus == 'En revisión':
            
            flash('Pago registrado correctamente', 'success')
            
        else:
            flash(f'El pago se encuentra en estatus: {pago_obj.estatus}', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar: {str(e)}', 'danger')
        
    return redirect(url_for('dynamic.table_view', table_name='pago'))

@pago_bp.route('/cancelar/<id>', methods=['GET', 'POST'])
def cancelar(id):
    try:
        pago_obj = Pago.query.get(uuid.UUID(id) if isinstance(id, str) else id)
        if pago_obj:
            pago_obj.estatus = "Cancelado" 
            
            gastos_ids = [detalle.id_gasto for detalle in pago_obj.detalles_gastos]

            for detalle in pago_obj.detalles_gastos:
                db.session.delete(detalle)
            
            db.session.flush()

            for g_id in gastos_ids:
                FinanzasService.actualizar_estatus_gasto(g_id)
            
            db.session.commit()
            flash('Pago cancelado', 'success')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar pago: {str(e)}', 'danger')
        
    return redirect(url_for('dynamic.table_view', table_name='pago'))