from django.contrib import admin
from .models import Usuario, Evento, Asistencia

admin.site.register(Usuario)
admin.site.register(Evento)
admin.site.register(Asistencia)