"""
Vista para renderizar el formulario de registro biométrico.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..services.firebase_service import firebase_service
from ..decorators import encargado_or_admin


@encargado_or_admin
def pagina_inicio(request):
    """Renderiza la página de inicio con opciones de ML y Reconocimiento"""
    # Obtener evento activo automáticamente
    evento = firebase_service.obtener_evento_activo()
    return render(request, 'inicio.html', {
        'evento': evento,
        'es_admin': request.user.is_staff
    })


@encargado_or_admin
def registro_biometrico(request):
    """Renderiza el formulario de registro biométrico"""
    return render(request, 'registro_biometrico.html')


@encargado_or_admin
def listar_usuarios_web(request):
    """Lista usuarios registrados (vista web) - filtra por estado activo/inactivo y búsqueda"""
    try:
        show_disabled = request.GET.get('disabled', 'false') == 'true'
        search_query = request.GET.get('search', '').strip()
        
        todos_usuarios = firebase_service.listar_usuarios()
        
        # Filtrar por búsqueda si existe
        if search_query:
            search_lower = search_query.lower()
            usuarios_filtrados = []
            for u in todos_usuarios:
                rut = str(u.get('rut', '')).lower()
                nombre = str(u.get('nombre', '')).lower()
                carrera = str(u.get('carrera', '')).lower()
                
                if (search_lower in rut or 
                    search_lower in nombre or 
                    search_lower in carrera):
                    usuarios_filtrados.append(u)
            todos_usuarios = usuarios_filtrados
        
        # Filtrar por estado activo/inactivo
        if show_disabled:
            usuarios = [u for u in todos_usuarios if not u.get('activo', True)]
        else:
            usuarios = [u for u in todos_usuarios if u.get('activo', True)]
        
        return render(request, 'lista_usuarios.html', {
            'usuarios': usuarios,
            'total': len(usuarios),
            'show_disabled': show_disabled,
            'search_query': search_query
        })
    except Exception as e:
        return render(request, 'lista_usuarios.html', {
            'error': str(e),
            'usuarios': [],
            'total': 0,
            'show_disabled': False,
            'search_query': ''
        })


@encargado_or_admin
@require_http_methods(["POST"])
def toggle_user_status(request, rut):
    """Habilita o deshabilita un usuario"""
    try:
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        if not usuario:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
        
        # Toggle del estado activo
        nuevo_estado = not usuario.get('activo', True)
        firebase_service.actualizar_usuario(rut, activo=nuevo_estado)
        
        estado_texto = 'habilitado' if nuevo_estado else 'deshabilitado'
        return JsonResponse({
            'success': True, 
            'message': f'Usuario {estado_texto} correctamente',
            'activo': nuevo_estado
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
