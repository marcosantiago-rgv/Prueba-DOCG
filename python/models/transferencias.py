import uuid
from datetime import datetime

from python.models import db
from python.models.sistema import BaseMixin, AuditMixin

# definimos la cabecera de la transferencia de inventario Representa la  operación que tendremos entre almacenes


class TransferenciaInventario(db.Model, BaseMixin, AuditMixin):
    # definimos como se llamra la tablaen la base de datos
    __tablename__ = "transferencia_inventario"

    id_almacen_origen = db.Column(
        db.UUID, db.ForeignKey("almacen.id"), nullable=False
    )
    id_almacen_destino = db.Column(
        db.UUID, db.ForeignKey("almacen.id"), nullable=False
    )
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # En revisión, Aprobado, Realizado
    estatus = db.Column(db.String(50), default="En revisión")

    almacen_origen = db.relationship(
        "Almacen",
        foreign_keys=[id_almacen_origen],
        backref="transferencias_salida",
        lazy=True,
    )
    almacen_destino = db.relationship(
        "Almacen",
        foreign_keys=[id_almacen_destino],
        backref="transferencias_entrada",
        lazy=True,
    )


class DetalleTransferenciaInventario(db.Model, BaseMixin, AuditMixin):
    # definimos como se llamra la tablaen la base de datos
    __tablename__ = "detalle_transferencia_inventario"

    id_transferencia = db.Column(
        db.UUID, db.ForeignKey("transferencia_inventario.id"), nullable=False
    )
    id_producto = db.Column(
        db.UUID, db.ForeignKey("productos.id"), nullable=False
    )
    cantidad = db.Column(db.Float, nullable=False, default=0)

    transferencia = db.relationship(
        "TransferenciaInventario",
        backref="detalles",
        lazy=True,
    )
    producto = db.relationship(
        "Productos",
        backref="detalles_transferencias",
        lazy=True,
    )
