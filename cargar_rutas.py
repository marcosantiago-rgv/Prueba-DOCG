#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:41:10 2025

@author: davidcontrerasgarza
"""

import pandas as pd 
import json
from datetime import datetime
import numpy as np
import os

working_directory='/Users/davidcontreras/Documents/Repositorios_RGV/Plantilla-Web-Apps-Flask/'
os.chdir(working_directory)
from app import *
from python.models import *


def rutas_inciales():
    # crear rutas iniciales
    data = [
        {'categoria':'Sistema','nombre': 'Acceso total', 'ruta': '/'},
        {'categoria':'Módulos','nombre': 'Archivos', 'ruta': '/files'},
        {'categoria':'Módulos','nombre': 'Auditoría', 'ruta': '/dynamic/logs_auditoria'},
        {'categoria':'Módulos','nombre': 'Dashboard operativo', 'ruta': '/dashboards/operative'},
        {'categoria':'Módulos','nombre': 'Dashboard estratégico', 'ruta': '/dashboards/strategic'},
        {'categoria':'Módulos','nombre': 'Reportes', 'ruta': '/dynamic/reportes'},
        {'categoria':'Módulos','nombre': 'Permisos', 'ruta': '/access_control'},
        {'categoria':'Tableros y reportes','nombre': 'SQL Reportes', 'ruta': '/report_queries'},
        {'categoria':'Tableros y reportes','nombre': 'SQL Tableros', 'ruta': '/dashboard_queries'},
    ]

    # Create the DataFrame
    rutas = pd.DataFrame(data)
    with app.app_context():
        id_usuario=Usuarios.query.filter_by(nombre="Sistema").first().id
        for i in range(len(rutas)):
            new_record = Rutas(categoria=rutas['categoria'][i],nombre=rutas['nombre'][i],ruta=rutas['ruta'][i],id_usuario=id_usuario)
            db.session.add(new_record)
        db.session.commit()

# funcion para crear rutas bases de tablas dinamicas
def crear_rutas_base(nombre_tabla):
    ruta='/dynamic/'+nombre_tabla.lower()
    data = [
        {'categoria':'Módulos','nombre': 'Acceso total '+nombre_tabla.replace('_',' '), 'ruta': ruta},
        {'categoria':'Acciones','nombre': 'Visualizar tabla de '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/view'},
        {'categoria':'Acciones','nombre': 'Visualizar datos de '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/data'},
        {'categoria':'Acciones','nombre': 'Visualizar formulario de '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/form'},
        {'categoria':'Acciones','nombre': 'Registrar información en '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/add'},
        {'categoria':'Acciones','nombre': 'Editar información en '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/edit'},
        {'categoria':'Acciones','nombre': 'Eliminar información en '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/delete'},
        {'categoria':'Acciones','nombre': 'Acceso a visulizar archivos '+nombre_tabla.replace('_',' '), 'ruta': f'{ruta}/files'}
    ]
    rutas = pd.DataFrame(data)
    with app.app_context():
        id_usuario=Usuarios.query.filter_by(nombre="Sistema").first().id
        for i in range(len(rutas)):
            new_record = Rutas(categoria=rutas['categoria'][i],nombre=rutas['nombre'][i],ruta=rutas['ruta'][i],id_usuario=id_usuario)
            db.session.add(new_record)
        db.session.commit()

# funcion para crear flujos de modulos
def crear_ruta(blueprint,actions):
    ruta='/'+blueprint
    data=[{'categoria':'Flujos','nombre': 'Acceso a total a flujos: '+blueprint.replace('_',' '), 'ruta': ruta}]
    for i in actions:
        new_route={'categoria':'Flujos','nombre': 'Acceso a '+i+' en '+blueprint.replace('_',' '), 'ruta': ruta+'/'+i}
        data.append(new_route)

    rutas = pd.DataFrame(data)
    with app.app_context():
        id_usuario=Usuarios.query.filter_by(nombre="Sistema").first().id
        for i in range(len(rutas)):
            new_record = Rutas(categoria=rutas['categoria'][i],nombre=rutas['nombre'][i],ruta=rutas['ruta'][i],id_usuario=id_usuario)
            db.session.add(new_record)
        db.session.commit()

# funcion para crear rutas de formularios
def crear_admin():
    with app.app_context():
        if db.session.is_active:
            db.session.rollback()
        #rol
        rol = [
            {'id_visualizacion':int(1),'nombre': 'Sistema', 'estatus': 'Activo'}
        ]
        rol = pd.DataFrame(rol)
        for i in range(len(rol)):
            new_record = Roles(id_visualizacion=int(rol['id_visualizacion'][i]),nombre=rol['nombre'][i],estatus=rol['estatus'][i])
            db.session.add(new_record)
        # usuario admin
        usuario = [
            {'id_visualizacion':int(1),'nombre': 'Sistema','correo_electronico':'david.contreras@rgvsoluciones.com','contrasena':'123','ultimo_cambio_de_contrasena':'2025-09-09','estatus': 'Activo'}
        ]
        usuario = pd.DataFrame(usuario)
        for i in range(len(usuario)):
            new_record = Usuarios(id_visualizacion=int(usuario['id_visualizacion'][i]),ultimo_cambio_de_contrasena=usuario['ultimo_cambio_de_contrasena'][i],nombre=usuario['nombre'][i],correo_electronico=usuario['correo_electronico'][i],contrasena=usuario['contrasena'][i],estatus=usuario['estatus'][i])
            db.session.add(new_record)
        db.session.commit()

def agregar_acceso_admin():
    with app.app_context():
        id_rol=Roles.query.filter_by(nombre="Sistema").first().id
        id_ruta=Rutas.query.filter_by(ruta="/").first().id
        rol = Roles.query.get(id_rol)
        ruta = Rutas.query.get(id_ruta)
        rol.rutas.append(ruta)
        usuario=Usuarios.query.filter_by(nombre="Sistema").first()
        usuario.id_rol=rol.id
        db.session.commit()
'''
crear_admin()
rutas_inciales()
agregar_acceso_admin()

'''
crear_rutas_base('productos')
crear_rutas_base('proveedores')
crear_rutas_base('ordenes_de_compra')
crear_rutas_base('productos_en_ordenes_de_compra')


actions={'aprobar','cancelar','recibir','confirmar','cerrar'}
crear_ruta('ordenes_de_compra',actions)
