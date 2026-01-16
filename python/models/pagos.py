import uuid
from datetime import datetime
from python.models import db
from python.models.sistema import BaseMixin, AuditMixin


class Pago(db.Model, BaseMixin, AuditMixin):
    id_gasto = db.Column(db.UUID, db.ForeignKey("gasto.id"), nullable=True)
    id_orden_de_compra = db.Column(db.UUID, db.ForeignKey(
        "ordenes_de_compra.id"), nullable=True)
    id_cuenta = db.Column(db.UUID, db.ForeignKey("cuenta_banco.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False, default=0)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # En revisión, Aprobado, Pagado, Cancelado
    estatus = db.Column(db.String(50), default="En revisión")
    referencia = db.Column(db.String(255), nullable=True)
    gasto = db.relationship("Gasto", backref="pagos", lazy=True)
    orden_de_compra = db.relationship(
        "OrdenesDeCompra", backref="pagos", lazy=True)
    cuenta = db.relationship("CuentaBanco", backref="todos_los_pagos", lazy=True)
    
