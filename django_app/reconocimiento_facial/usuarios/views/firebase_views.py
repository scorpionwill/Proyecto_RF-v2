"""
-----------------------------------------------------------------------------
Archivo: firebase_views.py
Descripcion: Controlador de API REST para operaciones CRUD de usuarios.
             Expone endpoints para listar, obtener, actualizar y eliminar
             usuarios en Firebase Firestore. Utilizado por el frontend
             JavaScript para operaciones asincronas.
Fecha de creacion: 15 de Noviembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from ..services.firebase_service import firebase_service


@csrf_exempt
@require_http_methods(["GET"])
def listar_usuarios_api(request):
    """
    Lista todos los usuarios de Firebase.
    
    Query params:
        - jornada: 'D' o 'N' (opcional)
        - buscar: texto de búsqueda (opcional)
    """
    try:
        jornada = request.GET.get('jornada')
        buscar = request.GET.get('buscar')
        
        if buscar:
            usuarios = firebase_service.buscar_usuarios(buscar)
        else:
            usuarios = firebase_service.listar_usuarios(jornada)
        
        return JsonResponse({
            'success': True,
            'count': len(usuarios),
            'usuarios': usuarios
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def obtener_usuario_api(request, rut):
    """Obtiene un usuario por RUT"""
    try:
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        
        if usuario:
            return JsonResponse({
                'success': True,
                'usuario': usuario
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'Usuario con RUT {rut} no encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def actualizar_usuario_api(request, rut):
    """Actualiza campos de un usuario"""
    try:
        data = json.loads(request.body)
        success = firebase_service.actualizar_usuario(rut, **data)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Usuario {rut} actualizado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'No se pudo actualizar usuario {rut}'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def eliminar_usuario_api(request, rut):
    """Elimina (desactiva) un usuario"""
    try:
        success = firebase_service.eliminar_usuario(rut)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Usuario {rut} eliminado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'No se pudo eliminar usuario {rut}'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
