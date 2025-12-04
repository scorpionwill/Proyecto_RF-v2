"""!/usr/bin/env python
Este archivo, manage.py, es una utilidad de línea de comandos que te permite 
interactuar con tu proyecto de Django. 
Lo usas para ejecutar tareas administrativas como iniciar el servidor de desarrollo, 
crear migraciones de base de datos y ejecutar pruebas."""
"""Utilidad de línea de comandos de Django para tareas administrativas."""
import os
import sys
try:
    import zoneinfo
except ImportError:
    try:
        from backports import zoneinfo
        sys.modules['zoneinfo'] = zoneinfo
    except ImportError:
        pass


def main():
    """Ejecutar tareas administrativas."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconocimiento_facial.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste "
            "activar un entorno virtual?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
