"""
Vista mejorada para captura de rostro con progreso en tiempo real.
Replica el comportamiento antiguo de capturar múltiples frames con barra de progreso.
"""
import cv2
import json
import base64
import time
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from ..services.firebase_service import firebase_service

LUCKFOX_IP = '172.32.0.93'
RTSP_URL_HIGH = f'rtsp://{LUCKFOX_IP}/live/0'
RTSP_URL_LOW = f'rtsp://{LUCKFOX_IP}/live/1'

@csrf_exempt
@require_http_methods(["POST"])
def capturar_rostro_luckfox(request):
    """
    Captura múltiples frames desde stream RTSP y extrae vector facial.
    Proceso similar al antiguo: 100 capturas con progreso.
    """
    import numpy as np
    import face_recognition
    
    try:
        # Parsear datos del request
        data = json.loads(request.body) if request.body else {}
        guardar = data.get('guardar', True)
        
        nombre = data.get('nombre', 'N/A')
        print(f"📸 Iniciando captura de 100 frames para: {nombre}")
        
        # Conectar al stream RTSP
        cap = cv2.VideoCapture(RTSP_URL_HIGH, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            return JsonResponse({
                'success': False,
                'message': 'No se pudo conectar al stream RTSP de LuckFox'
            }, status=500)
        
        # Variables para almacenar datos
        face_encodings_list = []
        captured_frames = []
        total_frames = 100
        frames_capturados = 0
        
        print(f"🎥 Capturando {total_frames} frames...")
        
        while frames_capturados < total_frames:
            ret, frame = cap.read()
            
            if not ret:
                print(f"⚠️ No se pudo leer frame {frames_capturados + 1}")
                continue
            
            # Convertir BGR a RGB para face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detectar rostros
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if len(face_locations) > 0:
                # Tomar el primer rostro detectado
                top, right, bottom, left = face_locations[0]
                
                # Extraer encoding del rostro
                face_encodings = face_recognition.face_encodings(rgb_frame, [face_locations[0]])
                
                if len(face_encodings) > 0:
                    face_encodings_list.append(face_encodings[0])
                    
                    # Dibujar rectángulo en el rostro
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"Captura {frames_capturados + 1}/{total_frames}", 
                               (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Guardar frame para muestra
                    if frames_capturados % 10 == 0:  # Guardar cada 10 frames
                        captured_frames.append(frame.copy())
                    
                    frames_capturados += 1
                    print(f"✅ Frame {frames_capturados}/{total_frames} capturado")
                else:
                    print(f"⚠️ No se pudo extraer encoding del frame")
            else:
                print(f"⚠️ No se detectó rostro en el frame")
            
            # Pequeña pausa para no saturar
            time.sleep(0.05)
        
        cap.release()
        print(f"🎉 Captura completada: {frames_capturados} frames")
        
        if len(face_encodings_list) < 10:
            return JsonResponse({
                'success': False,
                'message': f'Solo se capturaron {len(face_encodings_list)} rostros válidos. Se necesitan al menos 10.'
            }, status=400)
        
        # Calcular promedio de encodings para tener un vector representativo
        vector_promedio = np.mean(face_encodings_list, axis=0).tolist()
        
        print(f"✅ Vector promedio calculado: {len(vector_promedio)} dimensiones")
        
        # Convertir última imagen con rostro a base64
        if captured_frames:
            _, buffer = cv2.imencode('.jpg', captured_frames[-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
            imagen_base64 = base64.b64encode(buffer).decode('utf-8')
        else:
            imagen_base64 = None
        
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
