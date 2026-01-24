from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from python.models.modelos import db, Productos, Almacen, Existencia
from python.models.transferencias import TransferenciaInventario
from python.services.system.authentication import login_required, roles_required

transferencias_bp = Blueprint(
    'transferencias', __name__, url_prefix='/transferencias')


@transferencias_bp.route('/', methods=['GET'])
@login_required
@roles_required()
def listar_transferencias():
    # Redirigimos a la vista dinámica para que tenga el mismo look & feel
    # que otras tablas como ordenes_de_compra.
    return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))


@transferencias_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@roles_required()
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
    return render_template(
        'inventario/nueva_transferencia.html',
        productos=productos,
        almacenes=almacenes,
        activeMenu='inventario',
        activeItem='transferencias',
    )


@transferencias_bp.route('/actualizar_estado/<id>', methods=['POST'])
@login_required
@roles_required()
def actualizar_estado(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    nuevo_estado = request.form['estatus']
    transferencia.estatus = nuevo_estado
    db.session.commit()
    flash(f'Estado actualizado a {nuevo_estado}.')
    return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))


@transferencias_bp.route('/revision/<id>', methods=['GET', 'POST'])
@login_required
@roles_required()
def marcar_revision(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    transferencia.estatus = 'En revisión'
    db.session.commit()
    flash('Transferencia marcada en revisión.')
    return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))


@transferencias_bp.route('/aprobar/<id>', methods=['GET', 'POST'])
@login_required
@roles_required()
def aprobar_transferencia(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    if transferencia.estatus == 'En revisión':
        transferencia.estatus = 'Aprobado'
        db.session.commit()
        flash('Transferencia aprobada.', 'success')
    else:
        flash('Solo se pueden aprobar transferencias en revisión.', 'warning')
    return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))


@transferencias_bp.route('/realizar/<id>', methods=['GET', 'POST'])
@login_required
@roles_required()
def realizar_transferencia(id):
    transferencia = TransferenciaInventario.query.get_or_404(id)
    if transferencia.estatus != 'Aprobado':
        flash('Solo se pueden realizar transferencias aprobadas.')
        return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))
    # Actualiza existencias
    from python.models.inventario import Existencia
    # Buscar existencia en almacén origen
    existencia_origen = Existencia.query.filter_by(
        id_producto=transferencia.id_producto, id_almacen=transferencia.id_almacen_origen).first()

    # Opción 1: permitir realizar aunque no exista registro o no haya stock suficiente
    # Si no existe la fila de existencias en el almacén origen, la creamos en 0
    if not existencia_origen:
        existencia_origen = Existencia(
            id_producto=transferencia.id_producto,
            id_almacen=transferencia.id_almacen_origen,
            cantidad=0,
        )
        db.session.add(existencia_origen)

    # Descontamos la cantidad solicitada, permitiendo que quede en negativo si aplica
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
    flash('Transferencia realizada.')
    # flash('Transferencia realizada. El almacén origen puede quedar con existencias negativas.')
    return redirect(url_for('dynamic.table_view', table_name='transferencia_inventario'))


@transferencias_bp.route('/almacenes_origen', methods=['GET'])
@login_required
@roles_required()
def almacenes_origen_por_producto():
    """Devuelve los almacenes que tienen existencia positiva para el producto dado."""
    producto_id = request.args.get('producto_id')
    if not producto_id:
        return jsonify([])

    almacenes = (
        db.session.query(Almacen)
        .join(Existencia, Existencia.id_almacen == Almacen.id)
        .filter(
            Existencia.id_producto == producto_id,
            Existencia.cantidad > 0,
            Almacen.estatus == 'Activo',
        )
        .all()
    )

    data = [
        {
            "id": str(a.id),
            "nombre": a.nombre,
        }
        for a in almacenes
    ]
    return jsonify(data)
