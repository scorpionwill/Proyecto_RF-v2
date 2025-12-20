"""
-----------------------------------------------------------------------------
Archivo: urls.py
Descripcion: Configuracion de rutas URL del modulo usuarios. Define
             endpoints para autenticacion, gestion de usuarios, eventos,
             asistencias, reconocimiento facial, streaming RTSP, y
             API REST de Firebase.
Fecha de creacion: 25 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import usuario_views, evento_views, asistencia_views, reconocimiento_views, luckfox_views, firebase_views, web_views, usuario_api_views, luckfox_stream_limpio, admin_views

urlpatterns = [
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Gestión de Usuarios del Sistema (Admin)
    path('gestion/encargados/', admin_views.listar_encargados, name='listar_encargados'),
    path('gestion/encargados/crear/', admin_views.crear_encargado, name='crear_encargado'),
    path('gestion/encargados/eliminar/<int:user_id>/', admin_views.eliminar_encargado, name='eliminar_encargado'),
    
    # Página de inicio
    # Página de inicio
    path('', web_views.pagina_inicio, name='pagina_inicio'),
    
    # Páginas Web
    path('registro/', web_views.registro_biometrico, name='registro_biometrico'),
    path('usuarios/', web_views.listar_usuarios_web, name='listar_usuarios_web'),
    path('usuarios/<str:rut>/toggle/', web_views.toggle_user_status, name='toggle_user_status'),
    
    # URLs de Usuarios (legacy)
    path('usuarios/admin/', usuario_views.listar_usuarios, name='listar_usuarios'),
    path('crear_usuario/', usuario_views.crear_usuario, name='crear_usuario'),
    path('usuario/<str:rut>/credencial/', usuario_views.ver_credencial, name='ver_credencial'),
    path('usuario/<str:rut>/editar/', usuario_views.editar_usuario, name='editar_usuario'),
    path('capturar_imagenes/<int:usuario_id>/', usuario_views.capturar_imagenes, name='capturar_imagenes'),
    
    # URLs de Eventos
    path('eventos/', evento_views.listar_eventos, name='listar_eventos'),
    path('crear_evento/', evento_views.crear_evento, name='crear_evento'),
    path('evento/editar/<str:evento_id>/', evento_views.editar_evento, name='editar_evento'),
    path('evento/eliminar/<str:evento_id>/', evento_views.eliminar_evento, name='eliminar_evento'),
    path('evento/<str:evento_id>/descargar_planilla/', evento_views.descargar_planilla_evento, name='descargar_planilla_evento'),
    
    # URLs de Asistencias
    path('asistencias/', asistencia_views.listar_asistencias, name='listar_asistencias'),
    
    # URLs de Reconocimiento Facial
    path('entrenar_modelo/', reconocimiento_views.entrenar_modelo, name='entrenar_modelo'),
    path('reconocer_usuario/<str:evento_id>/', reconocimiento_views.reconocer_usuario, name='reconocer_usuario'),
    path('api/reconocimiento/capturar/', reconocimiento_views.capturar_y_reconocer, name='capturar_reconocer'),
    path('api/reconocimiento/confirmar_asistencia/', reconocimiento_views.confirmar_asistencia, name='confirmar_asistencia'),
    path('api/reconocimiento/registrar_manual/', reconocimiento_views.registrar_asistencia_manual, name='registrar_asistencia_manual'),
    
    # URLs de LuckFox
    path('api/luckfox/capturar/', luckfox_views.capturar_rostro_luckfox, name='capturar_luckfox'),
    path('api/luckfox/progreso/', luckfox_views.obtener_progreso_captura, name='progreso_captura'),
    path('api/luckfox/verificar/', luckfox_views.verificar_conexion_luckfox, name='verificar_luckfox'),
    path('luckfox/stream/', luckfox_views.luckfox_stream, name='luckfox_stream'),  # Stream CON detección
    path('luckfox/stream_limpio/', luckfox_stream_limpio.luckfox_stream_limpio, name='luckfox_stream_limpio'),  # Stream SIN detección
    # Nuevos endpoints para registro en 2 fases
    path('api/luckfox/capturar_foto/', luckfox_views.capturar_foto_perfil, name='capturar_foto_perfil'),
    path('api/luckfox/guardar_usuario/', luckfox_views.guardar_usuario_final, name='guardar_usuario_final'),

    
    # URLs de Firebase (CRUD de Usuarios)
    path('api/usuarios/', firebase_views.listar_usuarios_api, name='api_lista_usuarios'),
    # API para buscar usuario por RUT (debe ir ANTES de las rutas genéricas con <str:rut>)
    path('api/usuarios/buscar_por_rut/', usuario_api_views.buscar_usuario_por_rut, name='api_buscar_usuario_rut'),
    path('api/usuarios/<str:rut>/', firebase_views.obtener_usuario_api, name='api_obtener_usuario'),
    path('api/usuarios/<str:rut>/actualizar/', firebase_views.actualizar_usuario_api, name='api_actualizar_usuario'),
    path('api/usuarios/<str:rut>/eliminar/', firebase_views.eliminar_usuario_api, name='api_eliminar_usuario'),
    # API para actualizar foto
    path('api/usuarios/<str:rut>/actualizar_foto/', usuario_api_views.actualizar_foto_usuario, name='api_actualizar_foto'),
]