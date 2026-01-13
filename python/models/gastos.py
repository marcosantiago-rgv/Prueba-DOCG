import uuid
from datetime import datetime
from python.models import db
from python.models.sistema import BaseMixin, AuditMixin


class CategoriaGasto(db.Model, BaseMixin, AuditMixin):
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    estatus = db.Column(db.String(255), default="Activo")


class Gasto(db.Model, BaseMixin, AuditMixin):
    id_categoria = db.Column(db.UUID, db.ForeignKey(
        "categoria_gasto.id"), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    monto = db.Column(db.Float, nullable=False, default=0)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # En revisión, Aprobado, Pagado parcial, Pagado, Cancelado
    estatus = db.Column(db.String(50), default="En revisión")
    categoria = db.relationship("CategoriaGasto", backref="gastos", lazy=True)
