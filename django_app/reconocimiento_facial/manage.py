"""
-----------------------------------------------------------------------------
Archivo: manage.py
Descripcion: Utilidad de linea de comandos de Django para tareas
             administrativas. Permite iniciar servidor, crear migraciones,
             ejecutar pruebas y otras tareas de gestion del proyecto.
Fecha de creacion: 05 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
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
