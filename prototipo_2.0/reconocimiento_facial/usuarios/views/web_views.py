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
    """Lista todos los usuarios registrados (vista web)"""
    try:
        usuarios = firebase_service.listar_usuarios()
        return render(request, 'lista_usuarios.html', {
            'usuarios': usuarios,
            'total': len(usuarios)
        })
    except Exception as e:
        return render(request, 'lista_usuarios.html', {
            'error': str(e),
            'usuarios': [],
            'total': 0
        })
