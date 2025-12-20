"""
Vista para captura de rostro con progreso en tiempo real.
Replica el comportamiento antiguo: cámara solo activa durante captura, con progreso visible.
"""
import socket
import struct
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from ..services.firebase_service import firebase_service
from ..services.inspireface_service import inspireface_service
import cv2
import base64
import time
import numpy as np
import threading

# Configuración de conexión LuckFox
LUCKFOX_IP = '172.32.0.93'
LUCKFOX_PORT = 8080
SOCKET_TIMEOUT = 10

# Configuración RTSP
RTSP_URL_HIGH = f'rtsp://{LUCKFOX_IP}/live/0'
RTSP_URL_LOW = f'rtsp://{LUCKFOX_IP}/live/1'

# Variable global para compartir progreso de captura
capture_progress = {
    'active': False,
    'current': 0,
    'total': 100,  # ← Aumentado de 50 a 100
    'status': 'idle'
}
progress_lock = threading.Lock()


@csrf_exempt
@require_http_methods(["POST"])
def capturar_rostro_luckfox(request):
    """
    Captura rostros usando InspireFace.
    - Captura 10 frames de alta calidad.
    - Genera embeddings de 512 dimensiones.
    - Calcula el promedio de los embeddings.
    - Guarda SOLO 1 foto de perfil en disco.
    """
    global capture_progress
    
    try:
        data = json.loads(request.body) if request.body else {}
        guardar = data.get('guardar', True)
        nombre = data.get('nombre', 'N/A')
        
        # Reset progreso
        with progress_lock:
            capture_progress = {
                'active': True,
                'current': 0,
                'total': 100,  # Aumentado a 100 para máxima precisión
                'status': 'capturing'
            }
        
        print(f"📸 Iniciando captura InspireFace para: {nombre}")
        
        # Conectar al stream RTSP
        cap = cv2.VideoCapture(RTSP_URL_HIGH, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Buffer mínimo para reducir latencia
        
        if not cap.isOpened():
            with progress_lock:
                capture_progress['active'] = False
                capture_progress['status'] = 'error'
            return JsonResponse({
                'success': False,
                'message': 'No se pudo conectar al stream RTSP'
            }, status=500)
        
        embeddings_list = []
        best_frame = None
        frames_capturados = 0
        total_frames = 100  # 100 capturas para vector muy robusto
        intentos = 0
        max_intentos = 300  # Margen amplio
        
        print(f"🎥 Capturando {total_frames} vectores con InspireFace...")
        
        # Limpieza de buffer (2 frames para sincronización)
        print("⏱️ Sincronizando cámara...")
        for _ in range(2):
            cap.read()
            
        print("📸 ¡Iniciando captura!")
        
        while frames_capturados < total_frames and intentos < max_intentos:
            ret, frame = cap.read()
            intentos += 1
            
            if not ret:
                continue
            
            # Redimensionar a Full HD 1080p para calidad óptima
            frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_LINEAR)
            
            try:
                # Generar embedding con InspireFace
                embedding = inspireface_service.get_face_embedding(frame)
                
                if embedding:
                    
                    embeddings_list.append(embedding)
                    frames_capturados += 1
                    
                    # Guardamos el último frame válido como foto de perfil
                    best_frame = frame
                    
                    print(f"✅ Captura {frames_capturados}/{total_frames} OK")
                    
                    # Actualizar progreso
                    with progress_lock:
                        capture_progress['current'] = frames_capturados
                
            except Exception as e:
                # print(f"⚠️ No se detectó rostro: {e}")
                pass
                
 
        
        cap.release()
        
        # Verificar mínimo de capturas
        if len(embeddings_list) < 5:
            with progress_lock:
                capture_progress['active'] = False
                capture_progress['status'] = 'error'
            return JsonResponse({
                'success': False,
                'message': f'No se pudo detectar el rostro claramente. Intente mejorar la iluminación.'
            }, status=400)
        
        with progress_lock:
            capture_progress['status'] = 'completed'
        
        print(f"🎉 Captura completada: {len(embeddings_list)} vectores")
        
        # ==========================================
        # FILTRADO DE OUTLIERS Y PROMEDIO ROBUSTO
        # ==========================================
        
        embeddings_array = np.array(embeddings_list)
        
        # 1. Calcular vector mediano inicial (más robusto que promedio)
        vector_mediano = np.median(embeddings_array, axis=0)
        
        # 2. Calcular distancias de cada vector al mediano
        distancias = []
        for vec in embeddings_array:
            # Distancia euclidiana
            d = np.linalg.norm(vec - vector_mediano)
            distancias.append(d)
        distancias = np.array(distancias)
        
        # 3. Calcular MAD (Median Absolute Deviation)
        mad = np.median(np.abs(distancias - np.median(distancias)))
        
        # 4. Filtrar outliers (umbral: mediana + 2*MAD)
        # Si MAD es muy pequeño, usamos desviación estándar
        if mad < 1e-6:
            umbral = np.mean(distancias) + 2 * np.std(distancias)
        else:
            umbral = np.median(distancias) + 3 * mad
            
        indices_validos = distancias < umbral
        vectores_limpios = embeddings_array[indices_validos]
        
        print(f"🧹 Limpieza: {len(embeddings_array)} -> {len(vectores_limpios)} vectores (Eliminados: {len(embeddings_array) - len(vectores_limpios)})")
        
        # 5. Calcular promedio final de los vectores limpios
        if len(vectores_limpios) > 0:
            vector_final = np.mean(vectores_limpios, axis=0).tolist()
        else:
            # Fallback si filtramos todo (raro)
            vector_final = np.mean(embeddings_array, axis=0).tolist()
        
        print(f"✅ Vector promedio calculado: {len(vector_final)} dimensiones")
        
        # GUARDAR
        response_data = {
            'success': True,
            'vector_size': len(vector_final),
            'message': 'Captura exitosa'
        }
        
        if guardar and all(k in data for k in ['nombre', 'rut', 'carrera']):
            try:
                import os
                from django.conf import settings
                
                rut = data['rut'].replace('-', '_')
                
                # 1. NO GUARDAR EN DISCO LOCAL (Optimización)
                # user_dir = os.path.join(settings.MEDIA_ROOT, 'usuarios', rut)
                # os.makedirs(user_dir, exist_ok=True)
                
                # 2. GENERAR BASE64 PARA FIREBASE
                if best_frame is not None:
                    # Convertir a base64 para Firebase
                    ret, buffer = cv2.imencode('.jpg', best_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    imagen_base64 = base64.b64encode(buffer).decode('utf-8')
                    imagen_data_url = f"data:image/jpeg;base64,{imagen_base64}"
                    print(f"✅ Foto procesada para Firebase (sin guardar en disco)")
                else:
                    # Fallback (no debería pasar si hay embeddings)
                    imagen_data_url = None
                
                # 3. GUARDAR O ACTUALIZAR EN FIREBASE
                # Verificar si el usuario ya existe
                usuario_existente = firebase_service.obtener_usuario_por_rut(data['rut'])
                
                if usuario_existente:
                    # Usuario existe - actualizar vector facial e imagen
                    print(f"✅ Usuario {data['nombre']} ya existe, actualizando datos biométricos...")
                    firebase_service.actualizar_usuario(
                        data['rut'],
                        vector_facial=vector_final,
                        imagen=imagen_data_url
                    )
                    response_data['usuario_guardado'] = usuario_existente
                    response_data['message'] = f'Datos biométricos de {data["nombre"]} actualizados correctamente'
                    response_data['updated'] = True
                else:
                    # Usuario nuevo - crear
                    print(f"✅ Creando nuevo usuario {data['nombre']}...")
                    usuario = firebase_service.crear_usuario(
                        nombre=data['nombre'],
                        rut=data['rut'],
                        carrera=data['carrera'],
                        jornada=data.get('jornada', 'D'),
                        vector_facial=vector_final, # Vector de 512d
                        imagen_base64=imagen_data_url
                    )
                    response_data['usuario_guardado'] = usuario
                    response_data['message'] = f'Usuario {data["nombre"]} registrado con InspireFace'
                    response_data['updated'] = False
            except Exception as e:
                print(f"⚠️ Error guardando: {e}")
                import traceback
                traceback.print_exc()
                response_data['warning'] = str(e)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        with progress_lock:
            capture_progress['active'] = False
            capture_progress['status'] = 'error'
        print(f"❌ Error: {e}")
        return JsonResponse({
            'success': False,
            'message': f'Error al capturar: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def obtener_progreso_captura(request):
    """
    Endpoint para polling del progreso de captura.
    """
    with progress_lock:
        return JsonResponse({
            'active': capture_progress['active'],
            'current': capture_progress['current'],
            'total': capture_progress['total'],
            'status': capture_progress['status'],
            'percentage': int((capture_progress['current'] / capture_progress['total']) * 100) if capture_progress['total'] > 0 else 0
        })


@csrf_exempt
@require_http_methods(["GET"])
def verificar_conexion_luckfox(request):
    """Verifica RTSP disponible."""
    return JsonResponse({
        'success': True,
        'message': 'Stream RTSP disponible',
        'ip': LUCKFOX_IP,
        'rtsp_url': RTSP_URL_HIGH
    })


import threading
camera_lock = threading.Lock()

def luckfox_stream(request):
    """Stream RTSP con detección de rostros y latencia mínima."""
    def stream_generator():
        cap = None
        retry_count = 0
        max_retries = 3
        
        # Cargar clasificador de rostros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        while retry_count < max_retries:
            try:
                if cap is not None:
                    cap.release()
                
                print(f"🔌 Conectando a RTSP (intento {retry_count + 1}/{max_retries})...")
                
                # ALTA CALIDAD del stream, redimensionar a HD
                rtsp_url = RTSP_URL_HIGH  # 2592x1944 (máxima calidad)
                
                # Configuración optimizada
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                
                # OPTIMIZACIONES DE LATENCIA (sin perder calidad de imagen):
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Buffer mínimo (reduce retraso)
                cap.set(cv2.CAP_PROP_FPS, 30)        # 30 FPS para fluidez
                
                if not cap.isOpened():
                    print(f"❌ No se pudo abrir RTSP")
                    retry_count += 1
                    continue
                
                print(f"✅ Conectado: {rtsp_url} → redimensionando a 1920x1080 FHD")

                retry_count = 0
                
                frame_count = 0
                error_count = 0
                
                while True:
                    ret, frame = cap.read()
                    
                    if not ret:
                        error_count += 1
                        if error_count > 5:
                            print("🔄 Reconectando...")
                            break
                        continue
                    
                    error_count = 0
                    frame_count += 1
                    
                    # REDIMENSIONAR a Full HD 1080p (1920x1080)
                    # Usamos INTER_LINEAR que es más rápido para streaming en tiempo real
                    frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_LINEAR)
                    
                    # YA NO DETECTAMOS ROSTROS AQUÍ PARA MAYOR FLUIDEZ
                    # El stream es "limpio" y la detección se hace en el endpoint de reconocimiento
                    
                    # Codificar con MÁXIMA calidad
                    ret, buffer = cv2.imencode('.jpg', frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 95,  # ← Calidad 95 (excelente)
                        cv2.IMWRITE_JPEG_OPTIMIZE, 0   # Sin optimización (rápido)
                    ])

                    if not ret:
                        continue
                    
                    # if frame_count % 100 == 0:
                    #    print(f"📊 Frames: {frame_count}")
                    
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
            except Exception as e:
                print(f"❌ Error RTSP: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
            finally:
                if cap is not None and retry_count >= max_retries:
                    cap.release()
                    print("🔌 RTSP cerrado")

    return StreamingHttpResponse(stream_generator(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

# ==========================================
# NUEVOS ENDPOINTS - REGISTRO EN DOS FASES
# ==========================================

@csrf_exempt
@require_http_methods(["POST"])
def capturar_foto_perfil(request):
    """
    Captura instantánea de 1 frame del RTSP para foto de perfil.
    Resolución: 1280x720 (igual que todo el sistema)
    """
    try:
        print("📸 Capturando foto de perfil...")
        
        # Conectar al RTSP
        cap = cv2.VideoCapture(RTSP_URL_HIGH, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 300)
        
        if not cap.isOpened():
            return JsonResponse({
                'success': False,
                'error': 'No se pudo conectar al stream RTSP'
            }, status=500)
        
        # Buffer cleanup - limpiar más frames para asegurar imagen estable
        print("🔄 Limpiando buffer (30 frames)...") 
        
        # Descartar 30 frames para asegurar que la cámara se haya estabilizado
        for i in range(30):
            cap.read()
        
        # Ahora capturar el frame real
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo capturar frame válido'
            }, status=500)
        
        # Verificar que el frame no esté vacío (negro/blanco/gris)
        frame_mean = frame.mean()
        print(f"📊 Brillo promedio del frame: {frame_mean:.1f}")
        
        if frame_mean < 30:  # Frame muy oscuro, probablemente inválido
            return JsonResponse({
                'success': False,
                'error': f'Frame capturado está muy oscuro (brillo: {frame_mean:.1f}), intenta de nuevo'
            }, status=500)
        
        if frame_mean > 240:  # Frame muy claro/blanco, probablemente inválido
            return JsonResponse({
                'success': False,
                'error': f'Frame capturado está muy claro (brillo: {frame_mean:.1f}), intenta de nuevo'
            }, status=500)
        
        # Redimensionar a Full HD 1080p
        frame = cv2.resize(frame, (1920, 1080), interpolation=cv2.INTER_LINEAR)
        
        # Codificar a JPEG con calidad 95 para Firebase
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])

        
        if not ret:
            return JsonResponse({
                'success': False,
                'error': 'Error al codificar imagen'
            }, status=500)
        
        # Convertir a base64
        imagen_base64 = base64.b64encode(buffer).decode('utf-8')  # ← Correcto: buffer ya es bytes
        
        # Dimensiones fijas (sabemos que redimensionamos a 1920x1080)
        width, height = 1920, 1080
        
        print(f"✅ Foto capturada: {len(imagen_base64)/1024:.1f} KB ({width}x{height})")
        
        return JsonResponse({
            'success': True,
            'imagen': f"data:image/jpeg;base64,{imagen_base64}",
            'size_kb': len(imagen_base64) / 1024,
            'width': width,
            'height': height
        })
        
    except Exception as e:
        print(f"❌ Error capturando foto: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def guardar_usuario_final(request):
    """
    Guarda usuario en Firebase con vector_facial e imagen de perfil.
    Recibe: nombre, rut, carrera, jornada, vector_facial (list), imagen_base64
    """
    try:
        data = json.loads(request.body)
        
        # Validar campos requeridos
        required = ['nombre', 'rut', 'carrera', 'vector_facial', 'imagen_base64']
        if not all(k in data for k in required):
            return JsonResponse({
                'success': False,
                'error': f'Faltan campos requeridos: {required}'
            }, status=400)
        
        nombre = data['nombre']
        rut = data['rut']
        carrera = data['carrera']
        jornada = data.get('jornada', 'D')
        vector_facial = data['vector_facial']
        imagen_base64 = data['imagen_base64']
        
        print(f"💾 Guardando usuario: {nombre} ({rut})")
        
        # Guardar en Firebase
        usuario = firebase_service.crear_usuario(
            nombre=nombre,
            rut=rut,
            carrera=carrera,
            jornada=jornada,
            vector_facial=vector_facial,
            imagen_base64=imagen_base64
        )
        
        print(f"✅ Usuario guardado en Firebase: {rut}")
        
        return JsonResponse({
            'success': True,
            'usuario': usuario,
            'message': f'Usuario {nombre} registrado exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error guardando usuario: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
