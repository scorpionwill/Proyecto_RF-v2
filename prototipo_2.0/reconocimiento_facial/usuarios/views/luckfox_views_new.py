"""
Vista para capturar rostros desde el dispositivo LuckFox Pico Ultra W.
Captura 100 frames con progreso en tiempo real usando OpenCV.
"""
import socket
import struct
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from ..services.firebase_service import firebase_service
import cv2
import base64
import time
import numpy as np


# Configuración de conexión LuckFox
LUCKFOX_IP = '172.32.0.93'
LUCKFOX_PORT = 8080
SOCKET_TIMEOUT = 10  # segundos

# Configuración RTSP
RTSP_URL_HIGH = f'rtsp://{LUCKFOX_IP}/live/0'
RTSP_URL_LOW = f'rtsp://{LUCKFOX_IP}/live/1'


@csrf_exempt
@require_http_methods(["POST"])
def capturar_rostro_luckfox(request):
    """
    Captura múltiples frames desde stream RTSP.
    Proceso: 100 capturas con detección de rostro usando OpenCV Haar Cascade.
    """
    try:
        # Parsear datos del request
        data = json.loads(request.body) if request.body else {}
        guardar = data.get('guardar', True)
        
        nombre = data.get('nombre', 'N/A')
        print(f"📸 Iniciando captura de 100 frames para: {nombre}")
        
        # Cargar clasificador de rostros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Conectar al stream RTSP
        cap = cv2.VideoCapture(RTSP_URL_HIGH, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            return JsonResponse({
                'success': False,
                'message': 'No se pudo conectar al stream RTSP de LuckFox'
            }, status=500)
        
        # Variables para almacenar datos
        face_data_list = []
        captured_frames = []
        total_frames = 100
        frames_capturados = 0
        intentos = 0
        max_intentos = total_frames * 5
        
        print(f"🎥 Capturando {total_frames} frames...")
        
        while frames_capturados < total_frames and intentos < max_intentos:
            ret, frame = cap.read()
            intentos += 1
            
            if not ret:
                continue
            
            # Convertir a escala de grises para detección
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detectar rostros
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            if len(faces) > 0:
                # Tomar el primer rostro
                x, y, w, h = faces[0]
                
                # Extraer ROI del rostro
                face_roi = gray[y:y+h, x:x+w]
                face_roi_resized = cv2.resize(face_roi, (100, 100))
                
                # Guardar datos del rostro
                face_data_list.append(face_roi_resized.flatten())
                frames_capturados += 1
                
                # Guardar frame para muestra (cada 20)
                if frames_capturados % 20 == 0:
                    frame_copy = frame.copy()
                    cv2.rectangle(frame_copy, (x, y), (x+w, y+h), (0, 255, 0), 3)
                    cv2.putText(frame_copy, f"{frames_capturados}/{total_frames}", 
                               (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    captured_frames.append(frame_copy)
                
                if frames_capturados % 10 == 0:
                    print(f"✅ Progreso: {frames_capturados}/{total_frames} frames")
        
        cap.release()
        print(f"🎉 Captura completada: {frames_capturados} frames en {intentos} intentos")
        
        if len(face_data_list) < 10:
            return JsonResponse({
                'success': False,
                'message': f'Solo se capturaron {len(face_data_list)} rostros válidos. Se necesitan al menos 10. Asegúrate de estar frente a la cámara.'
            }, status=400)
        
        # Calcular promedio como "vector"
        vector_promedio = np.mean(face_data_list, axis=0).tolist()
        
        print(f"✅ Vector calculado: {len(vector_promedio)} dimensiones")
        
        # Convertir última imagen a base64
        imagen_base64 = None
        if captured_frames:
            _, buffer = cv2.imencode('.jpg', captured_frames[-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
            imagen_base64 = base64.b64encode(buffer).decode('utf-8')
        
        response_data = {
            'success': True,
            'vector': vector_promedio,
            'vector_size': len(vector_promedio),
            'frames_capturados': frames_capturados,
            'message': f'✓ {frames_capturados} frames capturados exitosamente'
        }
        
        # Guardar en Firebase
        if guardar and all(k in data for k in ['nombre', 'rut', 'carrera']):
            try:
                usuario = firebase_service.crear_usuario(
                    nombre=data['nombre'],
                    rut=data['rut'],
                    carrera=data['carrera'],
                    jornada=data.get('jornada', 'D'),
                    vector_facial=vector_promedio,
                    imagen_base64=f"data:image/jpeg;base64,{imagen_base64}" if imagen_base64 else None
                )
                response_data['usuario_guardado'] = usuario
                response_data['message'] = f'✓ Usuario {data["nombre"]} registrado exitosamente con {frames_capturados} capturas'
                print(f"✅ Usuario guardado en Firebase: {usuario.get('id', 'N/A')}")
            except Exception as e:
                print(f"⚠️ Error guardando en Firebase: {e}")
                import traceback
                traceback.print_exc()
                response_data['warning'] = f'Vector capturado pero no se pudo guardar en Firebase: {str(e)}'
        
        return JsonResponse(response_data)
        
    except Exception as e:
        print(f"❌ Error general en captura: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error al capturar rostro: {str(e)}'
        }, status=500)
