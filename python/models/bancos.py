import uuid
from datetime import datetime
from python.models import db
from python.models.sistema import BaseMixin, AuditMixin

class CuentaBanco(db.Model, BaseMixin, AuditMixin):
    nombre = db.Column(db.String(255), nullable=False)
    numero_cuenta = db.Column(db.String(50), nullable=False)
    banco = db.Column(db.String(255), nullable=False)
    saldo_inicial = db.Column(db.Float, nullable=False, default=0)
    saldo_actual = db.Column(db.Float, default=0.00)
    estatus = db.Column(db.String(255), default="Activo")
    
        

class MovimientoBancario(db.Model, BaseMixin, AuditMixin):
    id_cuenta = db.Column(db.UUID, db.ForeignKey(
        "cuenta_banco.id"), nullable=False)
    # Ingreso o Egreso de saldo
    tipo = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False, default=0)
    fecha = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    descripcion = db.Column(db.String(500), nullable=True)
    cuenta = db.relationship("CuentaBanco", backref="movimientos", lazy=True)
