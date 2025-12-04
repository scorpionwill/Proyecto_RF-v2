"""Vistas para gestión de eventos usando Firebase."""

from django.shortcuts import render, redirect
from django.contrib import messages
from ..services.firebase_service import firebase_service
from ..decorators import admin_required
from datetime import datetime


@admin_required
def listar_eventos(request):
    """Lista todos los eventos ordenados por fecha."""
    try:
        # Actualizar estados automáticamente antes de listar
        firebase_service.actualizar_estados_eventos()
        
        # Obtener eventos desde Firebase
        eventos = firebase_service.listar_eventos()
    except Exception as e:
        import traceback
        print(f"❌ ERROR CRÍTICO EN VISTA LISTAR_EVENTOS: {e}")
        traceback.print_exc()
        messages.error(request, f"Error listando eventos: {e}")
        return render(request, 'eventos_grid.html', {'lista_eventos_completa': []})


@admin_required
def crear_evento(request):
    """Crea un nuevo evento."""
    if request.method == 'POST':
        try:
            firebase_service.crear_evento(
                nombre=request.POST.get('nom_evento'),
                descripcion=request.POST.get('descripcion'),
                fecha=request.POST.get('fecha'),
                hora_inicio=request.POST.get('hora_inicio'),
                hora_fin=request.POST.get('hora_fin'),
                relator=request.POST.get('relator'),
                ubicacion=request.POST.get('ubicacion')
            )
            messages.success(request, "Evento creado correctamente")
            return redirect('listar_eventos')
        except Exception as e:
            messages.error(request, f"Error creando evento: {e}")
            
    return render(request, 'crear_evento.html')


@admin_required
def editar_evento(request, evento_id):
    """Edita un evento existente."""
    if request.method == 'POST':
        try:
            firebase_service.actualizar_evento(
                evento_id,
                nombre=request.POST.get('nom_evento'),
                descripcion=request.POST.get('descripcion'),
                fecha=request.POST.get('fecha'),
                hora_inicio=request.POST.get('hora_inicio'),
                hora_fin=request.POST.get('hora_fin'),
                relator=request.POST.get('relator'),
                ubicacion=request.POST.get('ubicacion')
            )
            messages.success(request, "Evento actualizado correctamente")
            return redirect('listar_eventos')
        except Exception as e:
            messages.error(request, f"Error actualizando evento: {e}")

    # GET: Obtener datos para el formulario
    evento = firebase_service.obtener_evento(evento_id)
    if not evento:
        messages.error(request, "Evento no encontrado")
        return redirect('listar_eventos')
        
    return render(request, 'editar_evento.html', {'evento': evento})


@admin_required
def eliminar_evento(request, evento_id):
    """Elimina un evento."""
    if request.method == 'POST':
        try:
            firebase_service.eliminar_evento(evento_id)
            messages.success(request, "Evento eliminado correctamente")
            return redirect('listar_eventos')
        except Exception as e:
            messages.error(request, f"Error eliminando evento: {e}")
            return redirect('listar_eventos')
    
    # GET: Pedir confirmación
    evento = firebase_service.obtener_evento(evento_id)
    if not evento:
        messages.error(request, "Evento no encontrado")
        return redirect('listar_eventos')
    
    return render(request, 'confirmar_eliminar_evento.html', {'evento': evento})
