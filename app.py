# app.py

from flask.json.provider import DefaultJSONProvider
from python.routes.ordenes_de_compra import ordenes_de_compra_bp
# import blueprint transferencias
from python.routes.transferencias import transferencias_bp
from python.routes.gastos import gasto_bp
from python.routes.pago import pago_bp
from python.routes.inventario import inventario_bp
from python.routes.system.access_control import access_control_bp
from python.routes.system.report_queries import report_queries_bp
from python.routes.dashboards import dashboards_bp
from python.routes.system.dashboard_queries import dashboard_queries_bp
from python.services.api import api_bp
from python.services.system.authentication import auth_bp
from python.routes.system.home import home_bp
from python.routes.system.files import files_bp
from python.routes.system.errors import errors_bp
from python.routes.system.dynamic_routes import dynamic_bp
import datetime as dt
import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, flash, g, redirect, session, url_for
from flask_migrate import Migrate
from sqlalchemy import event, inspect

from flask_session import Session
from python.services.system.audit import *
from python.models.modelos import db
from python.services.system.authentication import *
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from python.services.system.extensions import limiter
from python.services.system.extensions import csrf
from python.services.system.template_formats import *

# Cargar variables de entornoa
load_dotenv()

# Inicializar la Aplicación
app = Flask(__name__)

# Configuración de la Aplicacióna
app.secret_key = os.urandom(24)
csrf.init_app(app)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret_key")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

if os.environ.get("FLASK_ENV") == "development":
    app.config["WTF_CSRF_ENABLED"] = False
    app.config['SESSION_COOKIE_SECURE'] = False
    debug=True
else:
    debug=False
    
app.jinja_env.globals['can_access'] = can_access
app.jinja_env.filters["date_format"] = date_format
app.jinja_env.filters["commafy"] = commafy
app.jinja_env.filters["money_format"] = money_format
app.jinja_env.filters["title_format"] = title_format
app.jinja_env.filters["remove_numbers"] = remove_numbers
app.jinja_env.filters["local_time"] = local_time

# Configuración de la sesión
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(weeks=1)
Session(app)


@app.before_request
def make_session_permanent():
    """Hacer que la sesión sea permanente y respetar el tiempo de expiración."""
    session.permanent = True


# Configuración de Base de Datos
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar extensiones
db.init_app(app)
csrf.init_app(app)
migrate = Migrate(app, db)
Session(app)
limiter.init_app(app)


# Eventos para auditoría
event.listen(db.session, "before_flush", add_logs_audit)
event.listen(db.session, "after_flush", add_logs_post_flush)
event.listen(db.session, "after_commit", clear_audit_flag)

# Configuración del usuario en `g`


@app.before_request
def set_usuario_email():
    """Asigna el email del usuario autenticado a `g.usuario_email`."""
    g.usuario_email = session.get("correo", None)


# Configuración de Tests
@app.cli.command("test")
def run_tests():
    """Ejecuta los tests de la Aplicación."""
    print("\033[94mIniciando pruebas...\033[0m")

    from python.tests.test_cases import test_db_connection, test_health
    from python.tests.test_config import run_all_tests

    tests = [test_health, test_db_connection]
    errors = run_all_tests(tests)

    if errors:
        print(f"\n\033[91m{len(errors)} pruebas fallaron:\033[0m")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n\033[92m¡Todas las pruebas pasaron exitosamente!\033[0m")


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, dt.time):
            return obj.isoformat()
        if isinstance(obj, dt.date):
            return obj.isoformat()
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        return super().default(obj)


app.json = CustomJSONProvider(app)

# Registro de Blueprints

app.register_blueprint(errors_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(files_bp)
app.register_blueprint(dynamic_bp)
app.register_blueprint(api_bp)
app.register_blueprint(dashboard_queries_bp)
app.register_blueprint(dashboards_bp)
app.register_blueprint(report_queries_bp)
app.register_blueprint(access_control_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(transferencias_bp)  # register blueprint transferencias
app.register_blueprint(ordenes_de_compra_bp)
app.register_blueprint(gasto_bp) 
app.register_blueprint(pago_bp)

# Almacenar los nombres de las tablas en caché
TABLES_CACHE = {}


# Definir tablas a omitir
OMIT_TABLES = [
    f"alembic_version",
    f"logs_auditoria",
    f"archivos",
    f"logs_auditoria",
    f"relacion_rutas_usuarios",
    f"relacion_rutas_roles",
    f"usuarios",
    f"roles",
    f"rutas",
    f"reportes",
]


def load_table_names():
    """Carga los nombres de las tablas disponibles, excluyendo las especificadas en OMIT_TABLES."""
    global TABLES_CACHE
    engine = db.engine
    inspector = db.inspect(engine)

    # Filtrar solo tablas de la app
    filtered_tables = [
        table
        for table in inspector.get_table_names()
        if table not in OMIT_TABLES
    ]

    # Formatear nombres y almacenar en caché
    TABLES_CACHE = {
        table: table.replace("_", " ").title()
        for table in sorted(filtered_tables)
    }


# Solo cuando se inicia la app
with app.app_context():
    load_table_names()


@app.context_processor
def inject_table_names():
    """Inyecta las tablas pre-cargadas en las plantillas."""
    return {"table_names": TABLES_CACHE}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=debug)