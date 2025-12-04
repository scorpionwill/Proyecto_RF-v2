"""Vistas para gestión de asistencias usando Firebase."""

from django.shortcuts import render
from django.contrib import messages
from ..services.firebase_service import firebase_service
from ..decorators import encargado_or_admin


@encargado_or_admin
def listar_asistencias(request):
    """
    Lista registros de asistencia con opción de filtrar por evento.
    - Admin: Puede ver todos los eventos y filtrar
    - Encargado: Solo ve asistencias del evento activo
    """
    try:
        # Si es Encargado, solo mostrar evento activo
        if not request.user.is_staff:
            # Obtener evento activo
            evento_activo = firebase_service.obtener_evento_activo()
            
            if not evento_activo:
                # No hay evento activo
                context = {
                    'asistencias': [],
                    'eventos': [],
                    'evento_seleccionado': None,
                    'evento_nombre': None,
                    'stats': {},
                    'total_asistencias': 0
                }
                return render(request, 'listar_asistencias.html', context)
            
            # Obtener asistencias solo del evento activo
            evento_id = evento_activo['id']
            asistencias = firebase_service.listar_asistencias(id_evento=evento_id)
            
            # Enriquecer con jornada
            for a in asistencias:
                a['nombre_evento'] = evento_activo['nombre']
                if 'fecha_hora' in a:
                    a['fecha_hora'] = a['fecha_hora'].replace('T', ' ')[:19]
            
            context = {
                'asistencias': asistencias,
                'eventos': [evento_activo],  # Solo el evento activo
                'evento_seleccionado': evento_id,
                'evento_nombre': evento_activo['nombre'],
                'stats': {},
                'total_asistencias': len(asistencias)
            }
            
            return render(request, 'listar_asistencias.html', context)
        
        # ADMIN: Mostrar todos los eventos con filtro
        eventos = firebase_service.listar_eventos()
        evento_id = request.GET.get('evento')
        
        asistencias = firebase_service.listar_asistencias(id_evento=evento_id)
        
        # Enriquecer con nombres de eventos
        eventos_map = {e['id']: e['nombre'] for e in eventos}
        
        for a in asistencias:
            a['nombre_evento'] = eventos_map.get(a['id_evento'], 'Evento Desconocido')
            if 'fecha_hora' in a:
                a['fecha_hora'] = a['fecha_hora'].replace('T', ' ')[:19]

        # Estadísticas simples
        stats = {}
        if not evento_id:
            for a in asistencias:
                eid = a.get('id_evento')
                stats[eid] = stats.get(eid, 0) + 1
        
        # Obtener nombre del evento seleccionado
        evento_nombre = None
        if evento_id:
            evento_nombre = eventos_map.get(evento_id, 'Desconocido')
        
        context = {
            'asistencias': asistencias,
            'eventos': eventos,
            'evento_seleccionado': evento_id,
            'evento_nombre': evento_nombre,
            'stats': stats,
            'total_asistencias': len(asistencias)
        }
        
        return render(request, 'listar_asistencias.html', context)
        
    except Exception as e:
        messages.error(request, f"Error listando asistencias: {e}")
        return render(request, 'listar_asistencias.html', {'asistencias': [], 'eventos': []})
