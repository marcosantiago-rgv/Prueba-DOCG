from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from python.models.modelos import db, Productos, Almacen, Existencia
from python.models.transferencias import TransferenciaInventario, DetalleTransferenciaInventario
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
        id_almacen_origen = request.form['almacen_origen']
        id_almacen_destino = request.form['almacen_destino']
        id_producto = request.form['producto']
        cantidad = float(request.form['cantidad'])

        # Creamos la cabecera de la transferencia
        transferencia = TransferenciaInventario(
            id_almacen_origen=id_almacen_origen,
            id_almacen_destino=id_almacen_destino,
            estatus='En revisión',
        )
        db.session.add(transferencia)
        db.session.flush()  # obtenemos transferencia.id sin cerrar la transacción

        # Por ahora agregamos un solo producto como detalle.
        # Más adelante se puede extender el formulario para enviar N productos.
        detalle = DetalleTransferenciaInventario(
            id_transferencia=transferencia.id,
            id_producto=id_producto,
            cantidad=cantidad,
        )
        db.session.add(detalle)
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
    # Actualiza existencias para cada producto de la transferencia
    from python.models.inventario import Existencia

    for detalle in transferencia.detalles:
        # Buscar existencia en almacén origen para este producto
        existencia_origen = Existencia.query.filter_by(
            id_producto=detalle.id_producto,
            id_almacen=transferencia.id_almacen_origen,
        ).first()

        # Si no existe la fila de existencias en el almacén origen, la creamos en 0
        if not existencia_origen:
            existencia_origen = Existencia(
                id_producto=detalle.id_producto,
                id_almacen=transferencia.id_almacen_origen,
                cantidad=0,
            )
            db.session.add(existencia_origen)

        # Descontamos la cantidad solicitada
        existencia_origen.cantidad -= detalle.cantidad

        # Buscar existencia en almacén destino
        existencia_destino = Existencia.query.filter_by(
            id_producto=detalle.id_producto,
            id_almacen=transferencia.id_almacen_destino,
        ).first()

        if existencia_destino:
            existencia_destino.cantidad += detalle.cantidad
        else:
            existencia_destino = Existencia(
                id_producto=detalle.id_producto,
                id_almacen=transferencia.id_almacen_destino,
                cantidad=detalle.cantidad,
            )
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
