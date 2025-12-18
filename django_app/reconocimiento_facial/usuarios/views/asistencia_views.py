"""Vistas para gestión de asistencias usando Firebase."""

from django.shortcuts import render
from django.contrib import messages
from ..services.firebase_service import firebase_service
from ..decorators import encargado_or_admin


@encargado_or_admin
def listar_asistencias(request):
    """
    Lista registros de asistencia con filtros de fecha (año, mes, día).
    - Admin: Puede ver todas las asistencias y filtrar
    - Encargado: Solo ve asistencias del evento activo
    """
    try:
        from datetime import datetime
        
        # Obtener parámetro de búsqueda
        search_query = request.GET.get('search', '').strip()
        
        # Si es Encargado, solo mostrar evento activo
        if not request.user.is_staff:
            # Obtener evento activo
            evento_activo = firebase_service.obtener_evento_activo()
            
            if not evento_activo:
                # No hay evento activo
                context = {
                    'asistencias': [],
                    'total_asistencias': 0,
                    'search_query': ''
                }
                return render(request, 'listar_asistencias.html', context)
            
            # Obtener asistencias solo del evento activo
            evento_id = evento_activo['id']
            asistencias = firebase_service.listar_asistencias(id_evento=evento_id)
            
            # Enriquecer con datos
            for a in asistencias:
                a['nombre_evento'] = evento_activo['nombre']
                a['fecha_evento'] = evento_activo.get('fecha', '')
                if 'fecha_hora' in a:
                    a['fecha_hora'] = a['fecha_hora'].replace('T', ' ')[:19]
            
            context = {
                'asistencias': asistencias,
                'total_asistencias': len(asistencias),
                'search_query': ''
            }
            
            return render(request, 'listar_asistencias.html', context)
        
        # ADMIN: Filtros de fecha
        today = datetime.now()
        year_filter = request.GET.get('year', str(today.year))
        month_filter = request.GET.get('month', str(today.month))
        day_filter = request.GET.get('day', '')
        
        # Obtener todos los eventos y asistencias
        eventos = firebase_service.listar_eventos()
        todas_asistencias = firebase_service.listar_asistencias()
        
        # Crear mapa de eventos por ID
        eventos_map = {e['id']: e for e in eventos}
        
        # Enriquecer asistencias con datos del evento
        for a in todas_asistencias:
            evento = eventos_map.get(a.get('id_evento'))
            if evento:
                a['nombre_evento'] = evento.get('nombre', 'Desconocido')
                a['fecha_evento'] = evento.get('fecha', '')
            else:
                a['nombre_evento'] = 'Evento Desconocido'
                a['fecha_evento'] = ''
            if 'fecha_hora' in a:
                a['fecha_hora'] = a['fecha_hora'].replace('T', ' ')[:19]
        
        # Aplicar búsqueda por nombre de evento
        if search_query:
            search_lower = search_query.lower()
            todas_asistencias = [a for a in todas_asistencias if search_lower in a.get('nombre_evento', '').lower()]
        
        # Aplicar filtros de fecha
        asistencias_filtradas = todas_asistencias
        if year_filter:
            asistencias_filtradas = [a for a in asistencias_filtradas if a.get('fecha_evento', '').startswith(year_filter)]
        if month_filter and year_filter:
            mes_str = f"{year_filter}-{month_filter.zfill(2)}"
            asistencias_filtradas = [a for a in asistencias_filtradas if a.get('fecha_evento', '').startswith(mes_str)]
        if day_filter and month_filter and year_filter:
            fecha_str = f"{year_filter}-{month_filter.zfill(2)}-{day_filter.zfill(2)}"
            asistencias_filtradas = [a for a in asistencias_filtradas if a.get('fecha_evento', '') == fecha_str]
        
        # Calcular años disponibles (contar eventos únicos, no asistencias)
        years = {}
        for evento in eventos:
            fecha = evento.get('fecha', '')
            if fecha and len(fecha) >= 4:
                year = fecha[:4]
                years[year] = years.get(year, 0) + 1
        available_years = [{'year': y, 'count': c} for y, c in sorted(years.items(), reverse=True)]
        
        # Calcular meses disponibles (contar eventos únicos para el año seleccionado)
        meses_base = [
            {'num': 1, 'nombre': 'Enero'}, {'num': 2, 'nombre': 'Febrero'},
            {'num': 3, 'nombre': 'Marzo'}, {'num': 4, 'nombre': 'Abril'},
            {'num': 5, 'nombre': 'Mayo'}, {'num': 6, 'nombre': 'Junio'},
            {'num': 7, 'nombre': 'Julio'}, {'num': 8, 'nombre': 'Agosto'},
            {'num': 9, 'nombre': 'Septiembre'}, {'num': 10, 'nombre': 'Octubre'},
            {'num': 11, 'nombre': 'Noviembre'}, {'num': 12, 'nombre': 'Diciembre'}
        ]
        
        for mes in meses_base:
            count = 0
            for evento in eventos:
                fecha = evento.get('fecha', '')
                if fecha and len(fecha) >= 7:
                    if year_filter and fecha.startswith(year_filter):
                        try:
                            month_num = int(fecha.split('-')[1])
                            if month_num == mes['num']:
                                count += 1
                        except:
                            pass
            mes['count'] = count
        
        # Calcular días disponibles (contar eventos únicos para año y mes seleccionados)
        available_days = []
        if year_filter and month_filter:
            days = {}
            for evento in eventos:
                fecha = evento.get('fecha', '')
                mes_str = f"{year_filter}-{month_filter.zfill(2)}"
                if fecha.startswith(mes_str):
                    try:
                        day = int(fecha.split('-')[2])
                        days[day] = days.get(day, 0) + 1
                    except:
                        pass
            available_days = [{'day': d, 'count': c} for d, c in sorted(days.items())]
        
        context = {
            'asistencias': asistencias_filtradas,
            'total_asistencias': len(asistencias_filtradas),
            'search_query': search_query,
            'available_years': available_years,
            'available_months': meses_base,
            'available_days': available_days,
            'year_selected': int(year_filter) if year_filter else None,
            'month_selected': int(month_filter) if month_filter else None,
            'day_selected': int(day_filter) if day_filter else None,
        }
        
        return render(request, 'listar_asistencias.html', context)
        
    except Exception as e:
        messages.error(request, f"Error listando asistencias: {e}")
        return render(request, 'listar_asistencias.html', {'asistencias': [], 'total_asistencias': 0, 'search_query': ''})
