"""es el punto de entrada para los servidores web compatibles con WSGI 
(Web Server Gateway Interface). WSGI es el estándar para las aplicaciones 
web de Python y permite que tu proyecto Django se comunique con el servidor web."""
"""
Configuración de WSGI para el proyecto reconocimiento_facial.

Expone el llamable WSGI como una variable a nivel de módulo llamada ``application``.

Para más información sobre este archivo, vea
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconocimiento_facial.settings')

application = get_wsgi_application()
