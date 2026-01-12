# Explicación del Proyecto Flask

Este proyecto utiliza Flask como framework principal para el desarrollo de una aplicación web modular y escalable. A continuación, se explica la función de cada carpeta y archivo relevante, así como el flujo general de la aplicación.

## Estructura General

- **app.py**: Archivo principal que inicia la aplicación Flask, configura rutas y extensiones.
- **cargar_rutas.py**: Encargado de cargar rutas de manera dinámica o modular.
- **config.py**: Configuración global de la aplicación (variables de entorno, base de datos, etc).
- **Procfile**: Archivo para despliegue en plataformas como Heroku.
- **requirements.txt**: Lista de dependencias del proyecto.
- **test_email.py**: Pruebas relacionadas con el envío de correos electrónicos.

## Carpetas Principales

### python/

Contiene toda la lógica de negocio, modelos, rutas y servicios de la aplicación.

- **models/**: Modelos de datos (ORM, clases de base de datos, etc).
  - `administracion.py`, `catalogos.py`, `modelos.py`, `sistema.py`: Definen las entidades y relaciones de la base de datos.
- **routes/**: Define las rutas (endpoints) de la aplicación.
  - `dashboards.py`, `ordenes_de_compra.py`: Rutas específicas para dashboards y órdenes de compra.
- **system/**: Funciones y utilidades del sistema.
  - `access_control.py`: Control de acceso y permisos.
  - `dashboard_queries.py`, `report_queries.py`: Consultas SQL para dashboards y reportes.
  - `dynamic_routes.py`: Rutas generadas dinámicamente.
  - `errors.py`: Manejo de errores personalizados.
  - `files.py`, `home.py`: Gestión de archivos y página principal.
- **services/**: Servicios auxiliares y lógica de negocio.
  - `api.py`: Integración con APIs externas.
  - **dynamic_functions/**: Funciones dinámicas para tablas, formularios y PDFs.
  - **form_workflows/**: Lógica de flujos de formularios (acciones al éxito, edición, etc).
  - **system/**: Servicios del sistema (autenticación, email, archivos, plantillas, etc).
- **tests/**: Pruebas unitarias y de integración.
  - `test_cases.py`, `test_config.py`: Casos de prueba para asegurar el correcto funcionamiento.

### static/

Archivos estáticos accesibles desde el frontend.

- **css/**: Hojas de estilo.
- **images/**: Imágenes usadas en la web.
- **js/**: Scripts JavaScript para lógica de frontend.

### templates/

Plantillas HTML renderizadas por Flask usando Jinja2.

- **main/**: Vistas principales (dashboards, etc).
- **partials/**: Fragmentos reutilizables (sidebar, header, tablas, etc).
- **system/**: Plantillas para formularios, tablas, errores, autenticación, etc.

### migrations/

Archivos de migración de base de datos gestionados por Alembic.

### flask_session/

Carpeta para almacenar sesiones de usuario si se usa Flask-Session.

### build/

Archivos generados (por ejemplo, CSS compilado de Tailwind).

### sql/

Consultas SQL organizadas por tipo y funcionalidad.

## Flujo General de la Aplicación

1. **Inicio**: `app.py` configura la app, carga rutas y extensiones.
2. **Rutas**: Las rutas en `python/routes/` y `python/system/dynamic_routes.py` definen los endpoints.
3. **Modelos**: Los modelos en `python/models/` gestionan la base de datos.
4. **Servicios**: Lógica de negocio y utilidades en `python/services/`.
5. **Frontend**: Flask renderiza plantillas desde `templates/` y sirve archivos de `static/`.
6. **Migraciones**: Cambios en la base de datos se gestionan con `migrations/`.
7. **Pruebas**: Se ejecutan desde `python/tests/`.

## Resumen

- **Backend**: Todo lo que está en `python/`, `migrations/`, `app.py`, `config.py`.
- **Frontend**: Todo lo que está en `templates/` y `static/`.

Este diseño permite separar claramente la lógica de backend y frontend, facilitando el mantenimiento y la escalabilidad del proyecto.
