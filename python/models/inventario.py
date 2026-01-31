import uuid
from python.models import db
from python.models.sistema import BaseMixin, AuditMixin


class Almacen(db.Model, BaseMixin, AuditMixin):
    nombre = db.Column(db.String(255), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=True)
    descripcion = db.Column(db.String(500), nullable=True)
    estatus = db.Column(db.String(255), default="Activo")


class Existencia(db.Model, BaseMixin, AuditMixin):
    id_producto = db.Column(db.UUID, db.ForeignKey(
        "productos.id"), nullable=False)
    id_almacen = db.Column(db.UUID, db.ForeignKey(
        "almacen.id"), nullable=False)
    cantidad = db.Column(db.Float, nullable=False, default=0)
    producto = db.relationship("Productos", backref="existencias", lazy=True)
    almacen = db.relationship("Almacen", backref="existencias", lazy=True)
