from flask import Blueprint, render_template, request, redirect, url_for, flash
from python.models.modelos import db, Productos, Almacen, Existencia
from python.models.transferencias import TransferenciaInventario

transferencias_bp = Blueprint(
    'transferencias', __name__, url_prefix='/transferencias')


@transferencias_bp.route('/', methods=['GET'])
def listar_transferencias():
    transferencias = TransferenciaInventario.query.order_by(
        TransferenciaInventario.fecha.desc()).all()
    return render_template('inventario/transferencias.html', transferencias=transferencias)


@transferencias_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_transferencia():
    productos = Productos.query.all()
    almacenes = Almacen.query.all()
    if request.method == 'POST':
        id_producto = request.form['producto']
        id_almacen_origen = request.form['almacen_origen']
        id_almacen_destino = request.form['almacen_destino']
        cantidad = float(request.form['cantidad'])
        transferencia = TransferenciaInventario(
            id_producto=id_producto,
            id_almacen_origen=id_almacen_origen,
            id_almacen_destino=id_almacen_destino,
            cantidad=cantidad,
            estatus='En revisión'
        )
        db.session.add(transferencia)
        db.session.commit()
        flash('Transferencia registrada en revisión.')
        return redirect(url_for('transferencias.listar_transferencias'))
    return render_template('inventario/nueva_transferencia.html', productos=productos, almacenes=almacenes)


@transferencias_bp.route('/actualizar_estado/<id>', methods=['POST'])
def actualizar_estado(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    nuevo_estado = request.form['estatus']
    transferencia.estatus = nuevo_estado
    db.session.commit()
    flash(f'Estado actualizado a {nuevo_estado}.')
    return redirect(url_for('transferencias.listar_transferencias'))


@transferencias_bp.route('/realizar/<id>', methods=['POST'])
def realizar_transferencia(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    if transferencia.estatus != 'Aprobado':
        flash('Solo se pueden realizar transferencias aprobadas.')
        return redirect(url_for('transferencias.listar_transferencias'))
    # Actualiza existencias
    from python.models.inventario import Existencia
    # Buscar existencia en almacén origen
    existencia_origen = Existencia.query.filter_by(
        id_producto=transferencia.id_producto, id_almacen=transferencia.id_almacen_origen).first()
    if not existencia_origen or existencia_origen.cantidad < transferencia.cantidad:
        flash('No hay suficiente existencia en el almacén origen.')
        return redirect(url_for('transferencias.listar_transferencias'))
    existencia_origen.cantidad -= transferencia.cantidad
    # Buscar existencia en almacén destino
    existencia_destino = Existencia.query.filter_by(
        id_producto=transferencia.id_producto, id_almacen=transferencia.id_almacen_destino).first()
    if existencia_destino:
        existencia_destino.cantidad += transferencia.cantidad
    else:
        existencia_destino = Existencia(id_producto=transferencia.id_producto,
                                        id_almacen=transferencia.id_almacen_destino, cantidad=transferencia.cantidad)
        db.session.add(existencia_destino)
    transferencia.estatus = 'Realizado'
    db.session.commit()
    flash('Transferencia realizada y existencias actualizadas.')
    return redirect(url_for('transferencias.listar_transferencias'))
