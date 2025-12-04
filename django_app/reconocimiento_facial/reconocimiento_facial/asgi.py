"""Es el punto de entrada para los servidores web compatibles con ASGI 
(Asynchronous Server Gateway Interface). ASGI es el sucesor de WSGI y 
permite que tu proyecto Django sea servido de forma asíncrona, lo cual es 
útil para aplicaciones que manejan muchas conexiones simultáneas o de larga duración."""

"""
Configuración de ASGI para el proyecto reconocimiento_facial.

Expone el llamable ASGI como una variable a nivel de módulo llamada ``application``.

Para más información sobre este archivo, vea
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconocimiento_facial.settings')

application = get_asgi_application()
