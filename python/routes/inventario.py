from flask import Blueprint, render_template, request, redirect, url_for, flash
from python.models.modelos import db, Productos, Almacen, Existencia

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')


@inventario_bp.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        nombre = request.form['nombre']
        unidad = request.form['unidad']
        nuevo = Productos(nombre=nombre, unidad_de_medida=unidad)
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado correctamente.')
        return redirect(url_for('inventario.productos'))
    productos_lista = Productos.query.all()
    return render_template('inventario/productos.html', productos=productos_lista)



@inventario_bp.route('/almacenes', methods=['GET'])
def almacenes():
    almacenes_lista = Almacen.query.all()
    return render_template('inventario/almacenes.html', almacenes=almacenes_lista)

@inventario_bp.route('/almacenes/nuevo', methods=['GET', 'POST'])
def nuevo_almacen():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ubicacion = request.form['ubicacion']
        nuevo = Almacen(nombre=nombre, ubicacion=ubicacion)
        db.session.add(nuevo)
        db.session.commit()
        flash('Almacén agregado correctamente.')
        return redirect(url_for('inventario.almacenes'))
    return render_template('inventario/nuevo_almacen.html')


@inventario_bp.route('/existencias', methods=['GET', 'POST'])
def existencias():
    productos_lista = Productos.query.all()
    almacenes_lista = Almacen.query.all()
    if request.method == 'POST':
        id_producto = request.form['producto']
        id_almacen = request.form['almacen']
        cantidad = float(request.form['cantidad'])
        nueva = Existencia(id_producto=id_producto,
                           id_almacen=id_almacen, cantidad=cantidad)
        db.session.add(nueva)
        db.session.commit()
        flash('Existencia registrada correctamente.')
        return redirect(url_for('inventario.existencias'))
    existencias_lista = Existencia.query.all()
    return render_template('inventario/existencias.html', existencias=existencias_lista, productos=productos_lista, almacenes=almacenes_lista)
