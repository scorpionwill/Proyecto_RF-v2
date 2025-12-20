"""
-----------------------------------------------------------------------------
Archivo: config.py
Descripcion: Define las constantes de configuracion para el sistema de
             reconocimiento facial. Incluye configuracion de camara RTSP,
             umbrales de similitud, tiempos de espera, y parametros de
             procesamiento de video e imagenes.
Fecha de creacion: 10 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""

# ==========================================
# Configuración de Cámara RTSP
# ==========================================
LUCKFOX_IP = '172.32.0.93'
LUCKFOX_PORT = 8080
RTSP_URL_HIGH = f'rtsp://{LUCKFOX_IP}/live/0'  # 2592x1944 (máxima calidad)
RTSP_URL_LOW = f'rtsp://{LUCKFOX_IP}/live/1'   # Baja resolución

# ==========================================
# Configuración de Procesamiento de Video
# ==========================================
VIDEO_RESOLUTION = (1920, 1080)  # Full HD
VIDEO_BUFFER_SIZE = 1
VIDEO_FPS = 30
JPEG_QUALITY = 95

# ==========================================
# Umbrales de Reconocimiento Facial
# ==========================================
# Umbrales de similitud de InspireFace (similitud coseno: 0-1)
SIMILARITY_THRESHOLD_DEFAULT = 0.48  # Umbral de coincidencia por defecto
SIMILARITY_THRESHOLD_STRICT = 0.60   # Umbral estricto para confirmación inmediata
SIMILARITY_THRESHOLD_VERIFICATION = 0.70  # Verificación 1:1

# Umbrales de detección
DETECTION_CONFIDENCE_THRESHOLD = 0.5  # Confianza mínima para detección
MIN_FACE_PIXEL_SIZE = 80  # Tamaño mínimo de rostro en píxeles
MAX_FACES_TO_DETECT = 5  # Máximo de rostros a detectar

# Umbrales de calidad
MIN_FACE_QUALITY = 0.3  # Puntaje mínimo de calidad para aceptar rostro

# ==========================================
# Configuración de Captura
# ==========================================
CAPTURE_FRAMES_COUNT = 10  # Número de frames a capturar para registro
CAPTURE_BUFFER_CLEANUP_FRAMES = 2  # Frames a descartar para estabilización
CAPTURE_MIN_VALID_FRAMES = 5  # Mínimo de capturas válidas requeridas
CAPTURE_MAX_ATTEMPTS = 60  # Máximo de intentos de captura

# Captura de foto de perfil
PROFILE_PHOTO_BUFFER_CLEANUP_FRAMES = 5

# ==========================================
# Configuración de Reconocimiento
# ==========================================
RECOGNITION_MAX_ATTEMPTS = 5  # Máximo de intentos de reconocimiento
RECOGNITION_PERSISTENCE_THRESHOLD = 2  # Confirmaciones de coincidencia necesarias

# ==========================================
# Configuración de Tiempos de Espera
# ==========================================
SOCKET_TIMEOUT = 10  # Tiempo de espera de socket en segundos
RTSP_CONNECTION_TIMEOUT = 30  # Tiempo de espera de conexión RTSP

# ==========================================
# Configuración de Base de Datos
# ==========================================
# Nombres de colecciones en Firebase
COLLECTION_USERS = 'usuarios'
COLLECTION_EVENTS = 'eventos'
COLLECTION_ATTENDANCE = 'asistencias'

# ==========================================
# Configuración de Filtrado de Outliers
# ==========================================
MAD_THRESHOLD_MULTIPLIER = 3  # Multiplicador para detección de outliers basada en MAD
STDDEV_THRESHOLD_MULTIPLIER = 2  # Multiplicador para detección de outliers basada en desviación estándar

# ==========================================
# Configuración de Logs
# ==========================================
LOG_EMOJI_ENABLED = True  # Usar emojis en logs de consola
LOG_VERBOSE_MATCHING = True  # Salida detallada durante el matching
