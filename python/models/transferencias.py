import uuid
from datetime import datetime
from python.models import db
from python.models.sistema import BaseMixin, AuditMixin


class TransferenciaInventario(db.Model, BaseMixin, AuditMixin):
    id_producto = db.Column(db.UUID, db.ForeignKey(
        "productos.id"), nullable=False)
    id_almacen_origen = db.Column(
        db.UUID, db.ForeignKey("almacen.id"), nullable=False)
    id_almacen_destino = db.Column(
        db.UUID, db.ForeignKey("almacen.id"), nullable=False)
    cantidad = db.Column(db.Float, nullable=False, default=0)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # En revisión, Aprobado, Realizado
    estatus = db.Column(db.String(50), default="En revisión")
    producto = db.relationship(
        "Productos", backref="transferencias", lazy=True)
    almacen_origen = db.relationship("Almacen", foreign_keys=[
                                     id_almacen_origen], backref="transferencias_salida", lazy=True)
    almacen_destino = db.relationship("Almacen", foreign_keys=[
                                      id_almacen_destino], backref="transferencias_entrada", lazy=True)
