"""
-----------------------------------------------------------------------------
Archivo: admin.py
Descripcion: Configuracion del panel de administracion Django.
             Registra los modelos Usuario, Evento y Asistencia para
             gestion desde el admin de Django.
Fecha de creacion: 08 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
from django.contrib import admin
from .models import Usuario, Evento, Asistencia

admin.site.register(Usuario)
admin.site.register(Evento)
admin.site.register(Asistencia)