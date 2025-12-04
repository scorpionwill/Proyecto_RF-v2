"""Vistas API para gestión de usuarios en Firebase"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from ..services.firebase_service import firebase_service
from ..decorators import encargado_or_admin



@csrf_exempt
@require_http_methods(["POST"])
def actualizar_foto_usuario(request, rut):
    """Actualiza la foto de perfil de un usuario en Firebase."""
    try:
        data = json.loads(request.body)
        imagen_base64 = data.get('imagen_base64')
        
        if not imagen_base64:
            return JsonResponse({'error': 'imagen_base64 requerida'}, status=400)
        
        print(f"💾 Actualizando foto de usuario {rut}")
        
        # Actualizar foto en Firebase
        firebase_service.actualizar_foto_usuario(rut, imagen_base64)
        
        print(f"✅ Foto actualizada para {rut}")
        
        return JsonResponse({
            'success': True,
            'message': 'Foto actualizada exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error actualizando foto: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@encargado_or_admin
def buscar_usuario_por_rut(request):
    """Busca un usuario por RUT y retorna sus datos."""
    rut = request.GET.get('rut')
    
    if not rut:
        return JsonResponse({'success': False, 'error': 'RUT requerido'}, status=400)
    
    try:
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        
        if usuario:
            return JsonResponse({
                'success': True,
                'usuario': {
                    'rut': usuario['rut'],
                    'nombre': usuario['nombre'],
                    'carrera': usuario.get('carrera', ''),
                    'jornada': usuario.get('jornada', 'D')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Usuario no encontrado'
            }, status=404)
            
    except Exception as e:
        print(f"❌ Error buscando usuario: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
