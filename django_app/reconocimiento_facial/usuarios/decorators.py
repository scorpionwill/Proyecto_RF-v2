"""Decoradores de permisos personalizados para el sistema."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    """
    Decorador que requiere que el usuario sea staff (Admin).
    Redirige a inicio si no tiene permisos.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('pagina_inicio')
        return view_func(request, *args, **kwargs)
    return wrapper


def encargado_or_admin(view_func):
    """
    Decorador que permite acceso a usuarios autenticados (Encargado o Admin).
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return wrapper
