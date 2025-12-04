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
        print(f"🔍 DEBUG: Total eventos recibidos de Firebase: {len(eventos)}")
        if eventos:
            print(f"🔍 DEBUG: Primer evento: {eventos[0]}")
        
        # Filtros básicos en memoria (Firebase tiene limitaciones de query complejos)
        year_filter = request.GET.get('year')
        month_filter = request.GET.get('month')
        semestre_filter = request.GET.get('semestre')
        
        # Obtener todos los eventos sin filtro primero para estadísticas
        todos_eventos = list(eventos)
        
        # Aplicar filtros combinados correctamente
        if year_filter and month_filter:
            # Filtro combinado: año Y mes
            try:
                month_num = int(month_filter)
                eventos = [e for e in eventos if e.get('fecha', '').startswith(year_filter) and int(e.get('fecha', '').split('-')[1]) == month_num]
            except (ValueError, IndexError):
                pass
        elif year_filter:
            # Solo filtro de año
            eventos = [e for e in eventos if e.get('fecha', '').startswith(year_filter)]
        elif month_filter:
            # Solo filtro de mes (todos los años)
            try:
                month_num = int(month_filter)
                eventos = [e for e in eventos if int(e.get('fecha', '').split('-')[1]) == month_num]
            except (ValueError, IndexError):
                pass
            
        if semestre_filter:
            def get_month(fecha_str):
                try:
                    return int(fecha_str.split('-')[1])
                except:
                    return 0
                
            if semestre_filter == 'otono':  # Marzo (3) - Julio (7)
                eventos = [e for e in eventos if 3 <= get_month(e.get('fecha', '')) <= 7]
            elif semestre_filter == 'primavera':  # Agosto (8) - Diciembre (12)
                eventos = [e for e in eventos if 8 <= get_month(e.get('fecha', '')) <= 12]

        # Obtener años disponibles con contadores
        years = {}
        for e in todos_eventos:
            try:
                fecha = e.get('fecha', '')
                if fecha:
                    year = fecha.split('-')[0]
                    years[year] = years.get(year, 0) + 1
            except:
                pass
        available_years = [{'year': y, 'count': c} for y, c in sorted(years.items(), reverse=True)]
        
        # Meses con nombres en español y contadores
        meses_base = [
            {'num': 1, 'nombre': 'Enero'},
            {'num': 2, 'nombre': 'Febrero'},
            {'num': 3, 'nombre': 'Marzo'},
            {'num': 4, 'nombre': 'Abril'},
            {'num': 5, 'nombre': 'Mayo'},
            {'num': 6, 'nombre': 'Junio'},
            {'num': 7, 'nombre': 'Julio'},
            {'num': 8, 'nombre': 'Agosto'},
            {'num': 9, 'nombre': 'Septiembre'},
            {'num': 10, 'nombre': 'Octubre'},
            {'num': 11, 'nombre': 'Noviembre'},
            {'num': 12, 'nombre': 'Diciembre'},
        ]
        
        # Calcular contadores por mes (considerando año si está seleccionado)
        for mes in meses_base:
            count = 0
            for e in todos_eventos:
                try:
                    fecha = e.get('fecha', '')
                    if fecha:
                        parts = fecha.split('-')
                        event_month = int(parts[1])
                        event_year = parts[0]
                        
                        # Si hay año seleccionado, contar solo eventos de ese año
                        if year_filter:
                            if event_year == year_filter and event_month == mes['num']:
                                count += 1
                        else:
                            # Sin año, contar todos los eventos de ese mes
                            if event_month == mes['num']:
                                count += 1
                except:
                    pass
            mes['count'] = count

        context = {
            'lista_eventos_completa': eventos,
            'available_years': available_years,
            'available_months': meses_base,
            'year_selected': int(year_filter) if year_filter else None,
            'month_selected': int(month_filter) if month_filter else None,
            'semestre_selected': semestre_filter,
        }
        print(f"🔍 DEBUG: Context eventos length: {len(context['lista_eventos_completa'])}")
        print(f"🔍 DEBUG: Context keys: {context.keys()}")
        return render(request, 'eventos_grid.html', context)
        
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
