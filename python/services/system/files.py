# python/services/files.py

import io

import pandas as pd
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.units import inch
from sqlalchemy.inspection import inspect
import io
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from svglib.svglib import svg2rlg
import os
from python.models import db
from python.services.system.helper_functions import *
from python.services.dynamic_functions.forms import *
from python.services.dynamic_functions.tables import *
from flask import request
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import aliased
from python.services.dynamic_functions.pdf import *

class ExcelService:
    @staticmethod
    def generate_excel(table_name,kind):
        """Exporta los datos de una tabla a un archivo Excel."""
        try:
            params = {}
            params['id_usuario'] = session['id_usuario']
            if kind=='model':
                model = get_model_by_name(table_name)
                query = model.query
                joins = get_joins()
                filtered_joins = {field: val for field, val in joins.items() if field in model.__table__.columns}
                aliased_name_columns = []
                for field, (table, id_column, name_column) in filtered_joins.items():
                    alias = aliased(table, name=f"{table.__tablename__}__{field}")
                    alias_id_col = getattr(alias, id_column.key)
                    query = query.outerjoin(alias, alias_id_col == getattr(model, field))
                    for col in table.__table__.columns:
                        alias_col = getattr(alias, col.key)
                        query = query.add_columns(alias_col.label(f"{field}_{col.key}"))
                        if col.key == name_column.key:
                            aliased_name_columns.append(alias_col)
                result = query.all()
                columns=get_columns(table_name,'main_page')
                if session['nombre_rol']=='Sistema':
                    columns.append('id')
                rows = [
                    {col: record_dict[col] for col in columns if col in record_dict}
                    for record_dict in (query_to_dict(record, model) for record in result)
                ]
            elif kind=='report':
                path = './static/sql/report_queries/'+table_name+'.sql'
                base_query = open(path, "r", encoding="utf-8").read()
                variables_query = extract_param_names(base_query)
                variables_request = {k: v for k, v in request.values.items() if k in variables_query and v != ""}
                result=db.session.execute(text(base_query),variables_request)
                rows = [dict(row) for row in result.mappings()]

            if not rows:
                return None, "La tabla no contiene datos."

            df = pd.DataFrame(rows)

            # Exportar a excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name=table_name)

            output.seek(0)
            return output.getvalue(), None
        except Exception as e:
            return None, str(e)


class PDFService:
    @staticmethod
    def generate_pdf(table_name, id_record):
        try:
            table_name = f"{table_name.split('/')[-1]}"
            # 1) Fetch parent record
            model = get_model_by_name(table_name)
            if not model:
                return jsonify({"error": f"La tabla '{table_name}' no existe."}), 404
            if table_name!='reportes':
                record=model.query.get(id_record)
                result=pdf(f'{table_name}',id_record)
                return result                
            else:
                record=model.query.get(id_record)
                result=pdf(f'reportes_{record.nombre.lower()}',id_record)
                return result

        except SQLAlchemyError as e:
            return None, f"Error de base de datos: {e}"
        except Exception as e:
            return None, str(e)
        