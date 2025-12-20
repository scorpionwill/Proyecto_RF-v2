"""
-----------------------------------------------------------------------------
Archivo: usuario_views.py
Descripcion: Controlador de gestion de usuarios registrados. Proporciona
             listado de usuarios, redireccion a registro biometrico,
             edicion de datos personales, y visualizacion de credenciales
             digitales con foto y datos del alumno.
Fecha de creacion: 05 de Noviembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from ..services.firebase_service import firebase_service
from ..decorators import admin_required


def listar_usuarios(request):
    """Lista todos los usuarios registrados desde Firebase."""
    try:
        usuarios = firebase_service.listar_usuarios()
        return render(request, 'listar_usuarios.html', {'usuarios': usuarios})
    except Exception as e:
        return render(request, 'listar_usuarios.html', {'usuarios': [], 'error': str(e)})


@admin_required
def crear_usuario(request):
    """
    Redirige a la vista de registro biométrico.
    La creación ahora se maneja en el flujo de registro biométrico.
    """
    return redirect('registro_biometrico')


@admin_required
def editar_usuario(request, rut):
    """Muestra formulario para editar usuario y cambiar foto de perfil."""
    try:
        # Obtener usuario actual desde Firebase por RUT
        usuarios = firebase_service.listar_usuarios()
        usuario = next((u for u in usuarios if u.get('rut') == rut), None)
        
        if not usuario:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        
        # Renderizar página de edición con datos actuales
        return render(request, 'editar_usuario.html', {
            'usuario': usuario,
            'rut': rut
        })
    except Exception as e:
        print(f"Error en editar_usuario: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def capturar_imagenes(request, usuario_id):
    """
    Deprecated: Ya no se usa captura local.
    Todo el proceso se maneja vía registro biométrico con LuckFox.
    """
    return redirect('registro_biometrico')


def ver_credencial(request, rut):
    """Muestra la credencial INACAP del usuario en modo solo lectura."""
    try:
        # Obtener usuario desde Firebase por RUT
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        
        if not usuario:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        
        # Renderizar página de credencial
        return render(request, 'ver_credencial.html', {
            'usuario': usuario
        })
    except Exception as e:
        print(f"Error en ver_credencial: {e}")
        return JsonResponse({'error': str(e)}, status=500)
