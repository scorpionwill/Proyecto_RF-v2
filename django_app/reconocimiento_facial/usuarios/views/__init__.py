# Este paquete contiene las vistas organizadas por funcionalidad

from . import (
    usuario_views,
    evento_views,
    asistencia_views,
    reconocimiento_views,
    luckfox_views,
    firebase_views,
    web_views,
    usuario_api_views,
    luckfox_stream_limpio,
    admin_views
)

__all__ = [
    'usuario_views',
    'evento_views',
    'asistencia_views',
    'reconocimiento_views',
    'luckfox_views',
    'firebase_views',
    'web_views',
    'usuario_api_views',
    'luckfox_stream_limpio',
    'admin_views'
]
