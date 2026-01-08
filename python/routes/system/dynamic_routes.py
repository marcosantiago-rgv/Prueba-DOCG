# python/routes/dynamic_routes.py

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for,session

from python.models import db
from python.models.modelos import *
from python.services.system.helper_functions import *
from python.services.form_workflows.edit_on_success import *
from python.services.form_workflows.on_success import *
from python.services.system.authentication import *
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.dynamic import AppenderQuery
from sqlalchemy.orm import aliased
from python.services.dynamic_functions.forms import *
from python.services.dynamic_functions.tables import *
from python.services.system.boto3_s3 import S3Service
from uuid import UUID
import pandas as pd

s3_service = S3Service()

# Crear un Blueprint para rutas dinámicas basado en el nombre de la tabla
dynamic_bp = Blueprint("dynamic", __name__, url_prefix="/dynamic")


###################
#  Table View
###################

@dynamic_bp.route("/<table_name>/view")
@login_required
@roles_required()
def table_view(table_name):
    parent_table=request.args.get("parent_table")
    id_parent_record=request.args.get("id_parent_record")
    """
    Ruta para listar todos los registros de una tabla de forma dinámica.
    """

    model = get_model_by_name(table_name)
    if not model:
        flash(f"La tabla '{table_name}' no existe.", "danger")
        return redirect(request.referrer or url_for("home.home"))

    # Obtener las columnas definidas en el modelo
    columns=get_columns(table_name,'main_page')
    if columns==None:
        columns = model.__table__.columns.keys()
        # Get Many-to-Many relationships
        many_to_many_columns = [
            rel.key for rel in model.__mapper__.relationships.values()  if rel.secondary is not None and "archivos" not in rel.key.lower() and "rutas" not in rel.key.lower()
        ]
        # Combine both lists
        columns = columns + many_to_many_columns

    # Datos para resaltar el menú activo en el sidebar
    if parent_table:
        parent_model = get_model_by_name(parent_table)
        module,active_menu=get_breadcrumbs(parent_table)
        parent_record=parent_model.query.get(id_parent_record)
        parent_record_name = getattr(parent_record, "nombre", None) or getattr(parent_record, "nombre_completo", None) or getattr(parent_record, "id_visualizacion", None)
        if module==parent_table.replace('_', ' ').capitalize():
            breadcrumbs=[{"name":parent_table.replace('_', ' ').capitalize(),"url":f"/dynamic/{parent_table}/view"},{"name":parent_record_name,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
        else:
            breadcrumbs=[{"name":module,"url":""},{"name":parent_table.replace('_', ' ').capitalize(),"url":f"/dynamic/{parent_table}/view"},{"name":parent_record_name,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
        context = {
                "activeMenu": active_menu, 
                "activeItem": parent_table,
                "breadcrumbs": breadcrumbs
            }
    else:
        module,active_menu=get_breadcrumbs(table_name)
        if module==table_name.replace('_', ' ').capitalize():
            breadcrumbs=[{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
        else:
            breadcrumbs=[{"name":module,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
        context = {
                "activeMenu": active_menu, 
                "activeItem": table_name,
                "breadcrumbs": breadcrumbs
            }
    number_buttons=get_table_buttons().get(table_name,0)
    date_variable=get_calendar_date_variable(table_name)
    relationships=get_table_relationships(table_name)
    data_tabs=get_data_tabs(table_name,parent_table,id_parent_record)
    checkbox=get_checkbox(table_name)
    return render_template(
        "system/dynamic_table.html",
        columns=columns,
        table_name=table_name,
        data_tabs=data_tabs,
        number_buttons=number_buttons,
        date_variable=date_variable,
        id_parent_record=id_parent_record,
        parent_table=parent_table,
        relationships=relationships,
        checkbox=checkbox,
        title_formats=TITLE_FORMATS,
        html='table',
        **context
    )

@dynamic_bp.route("/<table_name>/data", methods=["GET"])
@login_required
@roles_required()
def data(table_name):
    parent_table=request.args.get("parent_table")
    id_parent_record=request.args.get("id_parent_record")
    model = get_model_by_name(table_name)
    if not model:
        return jsonify({"error": f"La tabla '{table_name}' no existe."}), 404

    # Obtener parámetros de consulta
    view = request.args.get("view", 50, type=int)
    search = request.args.get("search", "", type=str)
    sortField = request.args.get("sortField", "fecha_de_creacion", type=str)
    sortRule = request.args.get("sortRule", "desc", type=str)
    page = request.args.get("page", 1, type=int)
    status = request.args.get("status", "todos", type=str)
    dateRange=request.args.get("dateRange", "", type=str)
    categories=request.args.get("categories", "", type=str)

    query = model.query

    if session['nombre_rol']!='Administrador' and session['nombre_rol']!='Sistema':
        query=query.filter(model.id_usuario==session['id_usuario'])
              
    # Agregar joins condicionales
    joins = get_joins()
    filtered_joins = {field: val for field, val in joins.items() if field in model.__table__.columns}
    # We'll store ALIASED name columns here for search_table
    aliased_name_columns = []

    for field, (table, id_column, name_column) in filtered_joins.items():
        # alias per field
        alias = aliased(table, name=f"{table.__tablename__}__{field}")

        # bind columns to alias
        alias_id_col = getattr(alias, id_column.key)

        # join alias to BASE model using the FK on the base model column `field`
        query = query.outerjoin(alias, alias_id_col == getattr(model, field))

        # now add ALL columns from the joined table
        for col in table.__table__.columns:
            alias_col = getattr(alias, col.key)
            query = query.add_columns(alias_col.label(f"{field}_{col.key}"))

            if col.key == name_column.key:
                aliased_name_columns.append(alias_col)
    
    # Aplicar búsqueda
    if search:
        query = search_table(query, model, search, aliased_name_columns)

    if table_name=='archivos':
        query=query.filter(Archivos.id_registro==session['id_registro_tabla_origen'])
        
    if parent_table:
        for rel in model.__mapper__.relationships.values():
            if rel.mapper.local_table.name == parent_table:
                fk = f"id_{rel.key.lower()}"
                query=query.filter(getattr(model, fk)==id_parent_record)
                break

    status_field = get_variable_tabs(table_name)

    if status != 'todos':
        query = query.filter(getattr(model, status_field) == status)
    else:
        open_status=get_open_status(table_name)
        if open_status and hasattr(model,status_field):
            query = query.filter(getattr(model, status_field).in_(open_status))
    

    fecha_fields = get_date_fields() 

    if dateRange:
        try:
            start_str, end_str = dateRange.split(" to ")
            start_date = datetime.fromisoformat(start_str.strip())
            end_date = datetime.fromisoformat(end_str.strip())
        except ValueError:
            # fallback: single date or invalid format
            try:
                start_date = end_date = datetime.fromisoformat(dateRange.strip())
            except ValueError:
                start_date = end_date = None

        # If conversion worked, apply filters
        if start_date and end_date:
            # Add 1 day to end_date to include full end-day in range
            end_date = end_date + timedelta(days=1)

            conditions = []
            for field in fecha_fields:
                if hasattr(model, field):
                    col = getattr(model, field)
                    # Works for both Date and DateTime columns
                    conditions.append(col.between(start_date, end_date))

            if conditions:
                query = query.filter(or_(*conditions))

    if categories:
        if isinstance(categories, str):
            categories = [c.strip() for c in categories.split(",") if c.strip()]
        query = query.filter(getattr(model, "id_categoria").in_(categories))

    # Contar registros filtrados
    total = query.count()

    # Aplicar ordenamiento
    if sortField in [f"{fk}_{col.key}" for fk, (tbl, _, _) in filtered_joins.items() for col in tbl.__table__.columns]:
        query = query.order_by(
            text(f'"{sortField}" {"ASC" if sortRule == "asc" else "DESC"}')
        )

    # 2) Check if sorting on a base model column
    elif sortField in model.__table__.columns:
        column_attr = getattr(model, sortField)
        query = query.order_by(
            column_attr.asc() if sortRule == "asc" else column_attr.desc()
        )

    # 3) Fallback if invalid
    else:
        query = query.order_by(model.id.asc())


    # Aplicar paginación
    query = query.offset((page - 1) * view).limit(view)
    records = query.all()
    items = [query_to_dict(record,model) for record in records]
    return jsonify(
        {
            "items": items,
            "total": total,
            "pages": (total + view - 1) // view, 
            "totals": {},  
        }
    )

@dynamic_bp.route("/<table_name>/form", methods=["GET", "POST"])
@login_required
@roles_required()
def form(table_name):
    parent_table=request.args.get("parent_table")
    id_parent_record=request.args.get("id_parent_record")    
    model = get_model_by_name(table_name)
    if not model:
        flash(f"La tabla '{table_name}' no existe.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

    foreign_options = get_foreign_options()
    estatus_options =  get_estatus_options(table_name)
    foreign_options["estatus"] = estatus_options
    form_options=get_form_options(table_name)
    foreign_options = {**foreign_options, **form_options}
    # Add Many-to-Many relationships
    many_to_many_data = {}
    for attr_name, attr in model.__mapper__.relationships.items():
        if attr.secondary is not None:  # Ensures it's Many-to-Many
            related_model = attr.mapper.class_

            # Get selected values for the current record
            selected_items = []

            # Ensure selected_items is iterable
            if isinstance(selected_items, list) or hasattr(selected_items, '__iter__'):
                selected_ids = [item.id for item in selected_items]  
            else:
                selected_ids = [selected_items.id] if selected_items else []

            # Get all available options
            all_options = related_model.query.all()

            # Store in dictionary
            many_to_many_data[attr_name] = {
                "selected": selected_ids,
                "options": all_options
            }

    # Add Multiple choice fields
    multiple_choice_data=get_multiple_choice_data()

    modulo,active_menu=get_breadcrumbs(table_name)
    default_variable_values={}
    # edicion
    record_id = request.args.get("id")
    if record_id!=None:
        record = model.query.get(record_id)
        name = getattr(record, "nombre", None)
        flujo = request.args.get("accion", None, type=str)
        accion = (f"Editar registro: {name}" if name else "Editar registro: "+ str(record.id_visualizacion)) if flujo is None else (f"{flujo}: {name}" if name else f"{flujo}:"+ str(record.id_visualizacion))
        estatus = getattr(record, "estatus", None) if flujo is None else flujo
        ignored_columns=get_ignored_columns_edit(table_name,estatus)
        columns = [col for col in model.__table__.columns.keys() if col not in ignored_columns]
        non_mandatory_columns=get_non_mandatory_columns(table_name)
        required_fields=[col for col in columns if col not in non_mandatory_columns]
        if not record:
            flash(f"Registro con ID {record_id} no encontrado en '{table_name}'.", "danger")
            return redirect(request.referrer or url_for("dynamic.table_view", table_name=table_name))
        if record.estatus in get_non_edit_status() or table_name in get_no_edit_access():
            flash(f"Registro ya no se puede editar.", "info")
            return redirect(request.referrer or url_for("dynamic.table_view", table_name=table_name))
        javascript = os.path.exists(f'static/js/form_logic/edit/{table_name}.js')
    else:
        ignored_columns=get_ignored_columns(table_name)
        columns = [col for col in model.__table__.columns.keys() if col not in ignored_columns]
        non_mandatory_columns=get_non_mandatory_columns(table_name)
        required_fields=[col for col in columns if col not in non_mandatory_columns]
        default_variable_values=get_default_variable_values(table_name)
        accion="Registrar"
        record=None
        javascript = os.path.exists(f'static/js/form_logic/add/{table_name}.js')
    context = {
        "activeMenu": active_menu,
        "activeItem": table_name,
        "foreign_options": foreign_options,
        "breadcrumbs": [{"name":modulo,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":url_for("dynamic.table_view", table_name=table_name)},{"name":accion,"url":""}]
    }
    form_filters=get_form_filters(table_name)
    parent_record=get_parent_record(table_name)
    return render_template(
        "system/dynamic_form.html",
        columns=columns,
        required_fields=required_fields,
        table_name=table_name,
        many_to_many_data=many_to_many_data,
        multiple_choice_data=multiple_choice_data,
        action=accion,
        record=record,
        default_variable_values=default_variable_values,
        javascript=javascript,
        form_filters=form_filters,
        parent_record=parent_record,
        parent_table=parent_table,
        id_parent_record=id_parent_record,
        timedelta=timedelta,
        **context,
    )

@dynamic_bp.route("/<table_name>/add", methods=["POST"])
@login_required
@roles_required()
def add(table_name):
    parent_table=request.args.get("parent_table")
    id_parent_record=request.args.get("id_parent_record")    
    model = get_model_by_name(table_name)
    if not model:
        flash(f"La tabla '{table_name}' no existe.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))
    try:
        # Retrieve all form data (handling multi-select fields correctly)
        model_columns = model.__table__.columns.keys()
        data = {key: request.form.getlist(key) for key in request.form.keys() if key in model_columns}
        data.pop('archivo', None)
        data = sanitize_data(model, data)
        # Extract many-to-many fields (to process separately)
        relationship_data = {}
        normal_data = {}
        for key, value in data.items():
            attr = getattr(model, key, None)
            if isinstance(attr, InstrumentedAttribute) and hasattr(attr.property, "mapper"):
                # This is a relationship field
                relationship_data[key] = value  # Store for later processing
            else:
                # Normal field (use first value if it's a list with one element)
                normal_data[key] = value[0] if isinstance(value, list) and len(value) == 1 else value
        # Create new record with only normal fields first
        new_record = model(**normal_data)
        new_record.id_usuario = Usuarios.query.get(session["id_usuario"]).id
        if hasattr(model, 'id_visualizacion'):
            new_record.id_visualizacion=get_id_visualizacion(table_name)
        if table_name=='archivos':
            new_record.tabla_origen=session['tabla_origen']
            new_record.id_registro=session['id_registro_tabla_origen']
            new_record.ruta_s3=''
            new_record.nombre=''
        if table_name=='usuarios':
            alphabet = string.ascii_letters + string.digits
            contrasena = ''.join(secrets.choice(alphabet) for i in range(20))
            new_record.contrasena=generate_password_hash(contrasena)
            new_record.ultimo_cambio_de_contrasena=datetime.today()
            new_user_email(new_record.correo_electronico,contrasena)
        db.session.add(new_record)
        db.session.flush()
        if table_name=='archivos':
            archivo = request.files.get("archivo")
            s3_service.upload_file(archivo, new_record.id,session['tabla_origen'])
            new_record.ruta_s3=f"{session['tabla_origen']}/{ new_record.id}_{archivo.filename}"
            new_record.nombre=archivo.filename
        # Process many-to-many relationships
        for key, value in relationship_data.items():
            related_model = getattr(model, key).property.mapper.class_
            # Convert IDs to actual objects
            selected_items = db.session.query(related_model).filter(related_model.id.in_([int(v) for v in value if v])).all()
            # Assign relationship
            getattr(new_record, key).extend(selected_items)
        # archivos
        archivos = [file for key, file in request.files.items() if key.startswith("id_archivo")]
        if archivos:
            for archivo in archivos:
                if archivo.filename:
                    # create file in archivos
                    new_file=Archivos(
                        nombre_del_archivo=archivo.name,
                        tabla_origen=table_name,
                        id_registro=new_record.id,
                        ruta_s3='',
                        nombre='',
                        id_usuario=session['id_usuario']
                    )      
                    db.session.add(new_file)
                    db.session.flush()
                    s3_service.upload_file(archivo, new_file.id,table_name)
                    new_file.ruta_s3=f"{table_name}/{new_file.id}_{archivo.filename}"
                    new_file.nombre=archivo.filename
                    db.session.add(new_file)
                    setattr(new_record, archivo.name, f'{new_file.id}__{archivo.filename}')       
        # Commit transaction
        on_success(table_name,new_record.id)
        db.session.commit()
        flash(f"Registro creado exitosamente en '{table_name.replace('_', ' ').capitalize()}'.", "success")    
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear el registro: {str(e)}", "danger")
        return(request.referrer or "/")
    if table_name=='archivos':
        return redirect(url_for("dynamic.table_view_files", table_name=session['tabla_origen'],id=session['id_registro_tabla_origen']))
    else:
        url=get_url_after_add(table_name)
        if 'double_table_view' in url:
            return redirect(url_for(url, table_name=table_name,id=new_record.id))
        else:
            return redirect(url_for(url, table_name=table_name,parent_table=parent_table,id_parent_record=id_parent_record))

@dynamic_bp.route("/<table_name>/delete", methods=["POST"])
@login_required
@roles_required()
def delete(table_name):
    model = get_model_by_name(table_name)
    if not model:
        flash(f"La tabla '{table_name}' no existe.", "danger")
        return redirect(url_for("home.home"))

    record_id = request.args.get("id")  # Obtener como cadena
    if record_id is None:
        flash("No se especificó el ID del registro a eliminar.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

    # Determinar el tipo de la clave primaria
    primary_key_column = list(model.__table__.primary_key.columns)[0]
    if primary_key_column.type.python_type is int:
        try:
            record_id = int(record_id)
        except ValueError:
            flash("El ID del registro debe ser numérico.", "danger")
            return redirect(url_for("dynamic.table_view", table_name=table_name))

    record = model.query.get(record_id)
    if not record:
        flash(f"Registro con ID {record_id} no encontrado en '{table_name}'.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

    try:
        db.session.delete(record)
        db.session.commit()
        flash(f"Registro eliminado exitosamente en '{table_name.replace('_', ' ').capitalize()}'.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el registro: {str(e)}", "danger")

    return redirect(url_for("dynamic.table_view", table_name=table_name))

@dynamic_bp.route("/<table_name>/edit", methods=["GET", "POST"])
@login_required
@roles_required()
def edit(table_name):
    """
    Endpoint alternativo para editar un registro.
    Se espera recibir el ID del registro a editar mediante un parámetro de query (por ejemplo, ?id=22).
    """
    model = get_model_by_name(table_name)
    if not model:
        flash(f"La tabla '{table_name.replace('_', ' ').capitalize()}' no existe.", "danger")
        return redirect(url_for("home.home"))

    record_id = request.args.get("id")
    if record_id is None:
        flash("No se especificó el ID del registro a editar.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

    record = model.query.get(record_id)
    if not record:
        flash(f"Registro con ID {record_id} no encontrado en '{table_name}'.", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

    if request.method == "POST":
        try:
            # Convertir y sanitizar los datos enviados
            data = {key: request.form.getlist(key) for key in request.form.keys()}  # Ensure multi-select fields get all values
            data = sanitize_data(model, data)
            for key, value in data.items():
                if key != "fecha_de_creacion" and hasattr(record, key):
                        attr = getattr(record.__class__, key)
                        # Check if the field is a relationship (Many-to-Many)
                        if isinstance(attr, InstrumentedAttribute) and hasattr(attr.property, 'mapper'):
                            related_model = attr.property.mapper.class_
                            # Convert selected IDs to integers
                            selected_ids = [int(v) for v in value if v] if value else []
                            # Query related objects and update relationship
                            selected_items = db.session.query(related_model).filter(related_model.id.in_(selected_ids)).all()
                            getattr(record, key).clear()  # Clear existing relationships
                            getattr(record, key).extend(selected_items)  # Add new selections

                        else:
                            # Assign normal fields
                            setattr(record, key, value[0] if isinstance(value, list) and len(value) == 1 else value)
            # archivos
            archivos = [file for key, file in request.files.items() if key.startswith("id_archivo")]
            if archivos:
                for archivo in archivos:
                    if archivo.filename:
                        old_file=Archivos.query.filter_by(id_registro=record.id,nombre_del_archivo=archivo.name,tabla_origen=table_name).first()
                        if old_file:
                            s3_service.delete_file(old_file.ruta_s3)
                            db.session.delete(old_file)
                        # create file in archivos
                        new_record=Archivos(
                            nombre_del_archivo=archivo.name,
                            tabla_origen=table_name,
                            id_registro=record.id,
                            ruta_s3='',
                            nombre='',
                            id_usuario=session['id_usuario']
                        )      
                        db.session.add(new_record)
                        db.session.flush()
                        s3_service.upload_file(archivo, new_record.id,table_name)
                        new_record.ruta_s3=f"{table_name}/{new_record.id}_{archivo.filename}"
                        new_record.nombre=archivo.filename
                        db.session.add(new_record)
                        setattr(record, archivo.name, f'{new_record.id}__{archivo.filename}')   
            db.session.flush()
            edit_on_success(table_name,record.id)
            db.session.commit()
            flash(f"Registro actualizado exitosamente en '{table_name.replace('_', ' ').capitalize()}'.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el registro: {str(e)}", "danger")
        return redirect(url_for("dynamic.table_view", table_name=table_name))

@dynamic_bp.route("/<table_name>/data/<id_record>", methods=["GET"])
@login_required
@roles_required()
def record_data(table_name,id_record):
    model = get_model_by_name(table_name)
    if not model:
        return jsonify({"error": f"La tabla '{table_name}' no existe."}), 404
    # Iniciar la consulta
    query = model.query
    # Agregar joins condicionales
    joins = get_joins()
    filtered_joins = {field: val for field, val in joins.items() if field in model.__table__.columns}
    # We'll store ALIASED name columns here for search_table
    aliased_name_columns = []

    for field, (table, id_column, name_column) in filtered_joins.items():
        # alias per field
        alias = aliased(table, name=f"{table.__tablename__}__{field}")

        # bind columns to alias
        alias_id_col = getattr(alias, id_column.key)

        # join alias to BASE model using the FK on the base model column `field`
        query = query.outerjoin(alias, alias_id_col == getattr(model, field))

        # now add ALL columns from the joined table
        for col in table.__table__.columns:
            alias_col = getattr(alias, col.key)
            query = query.add_columns(alias_col.label(f"{field}_{col.key}"))

            if col.key == name_column.key:
                aliased_name_columns.append(alias_col)
    query=query.filter(model.id == id_record)
    records = query.all()
    columns_order= get_columns(table_name,'modal')
    record = [record_to_ordered_list(model,joins,record,columns_order) for record in records]
    relationships=get_table_relationships(table_name)
    if relationships!='':
        for i in relationships:
            record[0].append((i,'/dynamic/'+i+'/view?parent_table='+table_name+'&id_parent_record='+id_record))
    return jsonify(record)

###################
# Double Table View
###################

@dynamic_bp.route("/<string:table_name>/double_table/view/<id>")
@login_required
@roles_required()
def double_table_view(table_name,id):
    model = get_model_by_name(table_name)
    record = model.query.get(id)
    variables=get_variables_double_table_view(table_name)
    columns_first_table = variables.get('columns_first_table')
    columns_second_table = variables.get('columns_second_table')
    title_first_table= variables.get('title_first_table')
    title_second_table= variables.get('title_second_table')
    model_first_table=variables.get('model_first_table')
    model_second_table=variables.get('model_second_table')
    edit_fields=variables.get('edit_fields')
    required_fields=variables.get('required_fields')
    foreign_options = get_foreign_options()
    form_options=get_form_options(table_name)
    foreign_options = {**foreign_options, **form_options}
    details = []
    
    for detail in variables.get('details', []): 
        value = getattr(record, detail)

        # Handle related objects
        if hasattr(value, "nombre"):
            value = value.nombre
        if hasattr(value, "nombre_completo"):
            value = value.nombre_completo

        # Format money fields
        if any(word in detail.lower() for word in ["importe", "monto", "precio"]):
            try:
                # Safely cast to Decimal/float and format as money
                value = f"${float(value):,.2f}"
            except Exception:
                # fallback if value is not numeric
                value = str(value)

        result = f"{detail.replace('_',' ').capitalize().replace('Id visualizacion','ID')}: {value}"
        details.append(result)

    module,active_menu=get_breadcrumbs(table_name)
    context = {
                "activeMenu": active_menu, 
                "activeItem": table_name,
                "breadcrumbs": [{"name":module,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
            }
    return render_template(
        "system/dynamic_two_table_view.html",
        table_name=table_name,
        main_record=record,
        columns_first_table=columns_first_table,
        columns_second_table=columns_second_table,
        title_first_table=title_first_table,
        title_second_table=title_second_table,
        model_first_table=model_first_table,
        model_second_table=model_second_table,
        details=details,
        edit_fields=edit_fields,
        required_fields=required_fields,
        html='table',
        foreign_options=foreign_options,
        **context
    )

@dynamic_bp.route("/<string:table_name>/double_table/data/<string:table>/<id>", methods=["GET", "POST"])
@login_required
@roles_required()
def double_table_view_data(table,table_name,id):
    variables=get_variables_double_table_view(table_name)
    if table=='first':
        sql_name= variables.get('query_first_table')
    elif table=='second':
        sql_name= variables.get('query_second_table')

    path = f'./static/sql/double_table_queries/{table_name}/{sql_name}.sql'
    base_query = open(path, "r", encoding="utf-8").read()
    variables_request={'id_main_record':id}
    # --- dynamic table inputs ---
    search    = request.args.get("search", "", type=str)
    sortRule  = request.args.get("sortRule", "desc", type=str)
    sortField  = request.args.get("sortField", "fecha_de_creacion", type=str)

    # 1) get columns from the base query (no rows)
    #    Postgres syntax for subquery alias; adjust alias quoting for other DBs if needed
    probe_sql = text(f"SELECT * FROM ({base_query}) AS base_q LIMIT 0")
    probe_res = db.session.execute(probe_sql, variables_request)
    columns = list(probe_res.keys())

    # validate sort field
    sortDir = "ASC" if sortRule.lower() == "asc" else "DESC"

    # 2) build WHERE for search (case-insensitive). For Postgres, use ILIKE + CAST.
    where_clause = ""
    params = dict(variables_request)
    ands = []
    if search:
        like_param = f"%{search}%"
        params["search"] = like_param
        ors = " OR ".join([f"CAST({col} AS TEXT) ILIKE :search" for col in columns])
        ands.append(f"({ors})")

    where_clause = f"WHERE {' AND '.join(ands)}" if ands else ""

    # 4) data page
    data_sql = text(f"""
        SELECT *
        FROM ({base_query}) AS base_q
        {where_clause}
        ORDER BY {sortField} {sortDir}
    """)
    result = db.session.execute(data_sql, params)
    items = [rowmapping_to_dict(rm) for rm in result.mappings().all()]
    return jsonify({"items": items})

@dynamic_bp.route("/<string:main_table_name>/double_table/add/<string:first_table>/<string:second_table>/<id_main_record>/<id_record>", methods=[ "POST"])
@login_required
def double_table_add(main_table_name,first_table,second_table,id_main_record,id_record):
    if request.method == "POST":
        try:
            main_model=get_model_by_name(main_table_name)
            main_record = main_model.query.get(id_main_record)
            model=get_model_by_name(first_table)
            record = model.query.get(id_record)
            record_id=record.id if record else id_record
            new_record=add_record_double_table(main_table_name,second_table,main_record.id,record_id)
            db.session.add(new_record)
            db.session.flush()
            on_add_double_table(main_table_name,id_main_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"Error al agregar el registro: {str(e)}", "danger")
    return redirect(url_for("dynamic.double_table_view",table_name=main_table_name,id=id_main_record))

@dynamic_bp.route("/<string:main_table_name>/double_table/delete/<string:table_name>/<id_main_record>/<id>", methods=[ "POST"])
@login_required
def delete_double_table(main_table_name,table_name,id,id_main_record):
    if request.method == "POST":
        try:
            model=get_model_by_name(table_name)
            record = model.query.get(id)
            validation=validate_delete(table_name,id)
            if validation:
                on_delete_double_table(table_name,id)
                db.session.delete(record)
                db.session.flush()
                on_delete_double_table(main_table_name,id_main_record)
                db.session.commit()
                message=''
                status='success'                
            else:
                message='El registro no puede ser eliminado'
                status='warning'
        except Exception as e:
            db.session.rollback()
            flash(f"Error al eliminar el registro: {str(e)}", "danger")
        return jsonify({"status": status, "message": message})

@dynamic_bp.route("/<string:table_name>/double_table/update/<string:column>/<id>/", methods=["POST"])
@dynamic_bp.route("/<string:table_name>/double_table/update/<string:column>/<id>/<value>", methods=[ "POST"])
@login_required
@csrf.exempt
def double_table_update(table_name,column,id,value=0):
    try:
        value_warning=''
        model=get_model_by_name(table_name)
        record = model.query.get(id)
        validation=get_update_validation(table_name,record,column,value)
        if validation['status']==0:
            message=validation['message']
            status='warning'
            value_warning=validation['value_warning']
        else:
            setattr(record, column, value)
            db.session.flush()
            on_update_double_table(table_name,id)
            db.session.commit()
            message='El valor se ha actualizado correctamente.'
            status='success'
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar el valor: {str(e)}", "danger")
    return jsonify({"status": status, "message": message,"value":value_warning})

###############
#  Table View Input
###################

@dynamic_bp.route("/<string:main_table_name>/input_table/view/<id>")
@login_required
@roles_required()
def table_view_input(main_table_name,id):
    model = get_model_by_name(main_table_name)
    record = model.query.get(id)
    variables=get_variables_table_view_input(main_table_name)
    columns = variables.get('columns')
    table_title = variables.get('table_title')
    table_name = variables.get('table_name')
    edit_fields=variables.get('edit_fields')
    required_fields=variables.get('required_fields')
    foreign_options = get_foreign_options()
    form_options=get_form_options(table_name)
    foreign_options = {**foreign_options, **form_options}
    details = []
    for detail in variables.get('details', []): 
        value = getattr(record, detail)

        # Handle related objects
        if hasattr(value, "nombre"):
            value = value.nombre
        if hasattr(value, "nombre_completo"):
            value = value.nombre_completo

        # Format money fields
        if any(word in detail.lower() for word in ["importe", "monto", "precio"]):
            try:
                # Safely cast to Decimal/float and format as money
                value = f"${float(value):,.2f}"
            except Exception:
                # fallback if value is not numeric
                value = str(value)

        result = f"{detail.replace('_',' ').capitalize().replace('Id visualizacion','ID')}: {value}"
        details.append(result)
    module,active_menu=get_breadcrumbs(table_name)
    context = {
                "activeMenu": active_menu, 
                "activeItem": main_table_name,
                "breadcrumbs": [{"name":module,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":""}]
            }
    return render_template(
        "system/dynamic_table_input.html",
        table_name=table_name,
        main_table_name=main_table_name,
        main_record=record,
        columns=columns,
        table_title=table_title,
        html='table',
        edit_fields=edit_fields,
        required_fields=required_fields,
        foreign_options=foreign_options,
        details=details,
        **context
    )

@dynamic_bp.route("/<string:table_name>/input_table/data/<id>", methods=["GET", "POST"])
@login_required
@roles_required()
def table_view_input_data(table_name,id):
    variables=get_variables_table_view_input(table_name)
    sql_name= variables.get('query_table')
    path = f'./static/sql/input_table_queries/{table_name}/{sql_name}.sql'
    base_query = open(path, "r", encoding="utf-8").read()
    variables_request={'id_main_record':id}
    # --- dynamic table inputs ---
    search    = request.args.get("search", "", type=str)
    sortRule  = request.args.get("sortRule", "desc", type=str)

    probe_sql = text(f"SELECT * FROM ({base_query}) AS base_q LIMIT 0")
    probe_res = db.session.execute(probe_sql, variables_request)
    columns = list(probe_res.keys())

    sortField = 'fecha_de_creacion'
    sortDir = "ASC" if sortRule.lower() == "asc" else "DESC"

    # 2) build WHERE for search (case-insensitive). For Postgres, use ILIKE + CAST.
    where_clause = ""
    params = dict(variables_request)
    ands = []
    if search:
        like_param = f"%{search}%"
        params["search"] = like_param
        ors = " OR ".join([f"CAST({col} AS TEXT) ILIKE :search" for col in columns])
        ands.append(f"({ors})")

    where_clause = f"WHERE {' AND '.join(ands)}" if ands else ""

    # 4) data page
    data_sql = text(f"""
        SELECT *
        FROM ({base_query}) AS base_q
        {where_clause}
        ORDER BY {sortField} {sortDir}
    """)
    result = db.session.execute(data_sql, params)
    items = [rowmapping_to_dict(rm) for rm in result.mappings().all()]
    return jsonify(
        {
            "items": items,
        }
    )

@dynamic_bp.route("/<string:table_name>/input_table/confirm/<id>")
@login_required
@roles_required()
def table_view_input_confirm(table_name,id):
    variables = get_variables_table_view_input(table_name)
    url_confirm=variables.get('url_confirm')
    return redirect(url_for(url_confirm, id=id))

@dynamic_bp.route("/<string:table_name>/double_table/confirm/<id>")
@login_required
@roles_required()
def double_table_view_confirm(table_name,id):
    variables = get_variables_double_table_view(table_name)
    url_confirm=variables.get('url_confirm')
    return redirect(url_for(url_confirm, id=id))

###################
# Files View
###################

@dynamic_bp.route("/<string:table_name>/files/<id>", methods=["GET"])
@login_required
@roles_required()
def table_view_files(table_name,id):
    model = get_model_by_name(table_name)
    module,active_menu=get_breadcrumbs(table_name)
    record=model.query.get(id)
    try:
        name=record.nombre 
    except:
        name=record.id_visualizacion
    context = {
            "activeMenu": active_menu, 
            "activeItem": table_name,
            "breadcrumbs": [{"name":module,"url":""},{"name":table_name.replace('_', ' ').capitalize(),"url":url_for("dynamic.table_view", table_name=table_name)},{"name":name,"url":""},{"name":"Archivos","url":""}]
        }
    # Obtener las columnas definidas en el modelo
    columns = get_columns('archivos','main_page')
    
    session['tabla_origen']=table_name
    session['id_registro_tabla_origen']=record.id
    date_variable=''
    buttons_modal_exits = os.path.exists(f'templates/partials/table/modals/archivos.html')
    return render_template(
        "system/dynamic_table.html",
        buttons_modal_exits=buttons_modal_exits,
        table_buttons=True,
        number_buttons=1,
        columns=columns,
        id_registro_padre=record.id,
        table_name='archivos',
        title_formats=TITLE_FORMATS,
        date_variable=date_variable,
        **context
    )

###################
# Import data 
###################

@dynamic_bp.route("/import_data/<string:table_name>", methods=["POST"])
@login_required
@roles_required()
def import_data(table_name):
    file = request.files.get("archivo")
    if not file:
        flash("No se seleccionó ningún archivo.", "info")
        return redirect(url_for('dynamic.table_view', table_name=table_name))

    model = get_model_by_name(table_name)
    if model is None:
        return jsonify({'alert':'info','message': f"La tabla '{table_name}' no existe."})
    try:
        # --- Read file ---
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            return jsonify({'alert':'info','message': "El archivo debe ser CSV o XLSX."})
        map = TABLE_COLUMN_MAPS.get(table_name)
        if map:
            df.columns = df.columns.str.strip()

            # --- Auto detect table ---
            table_name = detect_table_from_columns(df.columns)
            if not table_name:
                return jsonify({
                    "alert": "error",
                    "message": "No se pudo detectar la tabla automáticamente."
                })
                
            model = get_model_by_name(table_name)
            column_map = TABLE_COLUMN_MAPS[table_name]
            # --- Rename columns ---
            if column_map:
                df = df.rename(columns=column_map)
        # --- Validate required columns ---
        model_columns = {c.name for c in model.__table__.columns}

        required_columns = {
            c.name
            for c in model.__table__.columns
            if not c.nullable and not c.primary_key
        }

        file_columns = set(df.columns)
        missing_cols = required_columns - file_columns - {
            'estatus', 'id_usuario', 'id', 'fecha_de_actualizacion',
            'fecha_de_creacion', 'id_visualizacion'
        }

        if missing_cols:
            return jsonify({'alert':'info','message': f"Faltan columnas requeridas: {', '.join(missing_cols)}"})

        # --- 🔥 Resolve all FKs with 1–N batch queries ---
        df = resolve_foreign_keys_bulk(model, df)
        # --- Insert rows ---
        for _, row in df.iterrows():
            clean = {c: row[c] for c in df.columns if c in model_columns}
            clean=sanitize_data(model, clean)
            record = model(**clean)
            record.id_visualizacion = get_id_visualizacion(table_name)
            record.id_usuario = session['id_usuario']
            db.session.add(record)

        db.session.commit()
        return jsonify({'alert':'success','message': f"Se importaron {len(df)} registros."})

    except Exception as e:
        db.session.rollback()
        return jsonify({'alert':'error','message': f"Error en la importación: {e}"})

###################
# Upload specific files
###################

@dynamic_bp.route("/upload_file/<string:table_name>/<id>/<column>", methods=["POST"])
@login_required
def upload_file(table_name,id,column):
    model=get_model_by_name(table_name)
    record=model.query.get(id)
    old_file=Archivos.query.filter_by(id_registro=id,nombre_del_archivo=column,tabla_origen=table_name).first()
    if old_file:
        s3_service.delete_file(old_file.ruta_s3)
        db.session.delete(old_file)
    # create file in archivos
    new_record=Archivos(
        nombre_del_archivo=column,
        tabla_origen=table_name,
        id_registro=id,
        ruta_s3='',
        nombre='',
        id_usuario=session['id_usuario']
    )
    archivo = request.files.get("archivo")
    db.session.add(new_record)
    db.session.flush()
    s3_service.upload_file(archivo, new_record.id,table_name)
    new_record.ruta_s3=f"{table_name}/{new_record.id}_{archivo.filename}"
    new_record.nombre=archivo.filename
    db.session.add(new_record)
    setattr(record, column, f'{new_record.id}__{archivo.filename}')
    db.session.commit()
    return jsonify({'alert':'success','message': f"El archivo se cargo exitosamente."})