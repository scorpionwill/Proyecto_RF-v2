"""Stream RTSP limpio SIN detección facial para captura de foto de perfil."""

from django.http import StreamingHttpResponse
import cv2
import time

def luckfox_stream_limpio(request):
    """
    Stream RTSP sin recuadros de detección.
    Solo para captura de foto de perfil (imagen limpia).
    """
    def generate():
        cap = None
        try:
            print("📹 Iniciando stream limpio (sin detección)")
            
            # Conectar al RTSP en alta calidad
            cap = cv2.VideoCapture('rtsp://172.32.0.93/live/0', cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 300)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    time.sleep(0.01)
                    continue
                
                # Redimensionar a 1280x720 HD (SIN detección)
                frame_resized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_LINEAR)
                
               # Codificar a JPEG con calidad 92
                ret, buffer = cv2.imencode('.jpg', frame_resized, [
                    cv2.IMWRITE_JPEG_QUALITY, 92,
                    cv2.IMWRITE_JPEG_OPTIMIZE, 0
                ])
                
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
        except GeneratorExit:
            print("📹 Stream limpio cerrado por cliente")
        except Exception as e:
            print(f"❌ Error en stream limpio: {e}")
        finally:
            if cap is not None:
                cap.release()
                print("📹 Stream limpio liberado")
    
    return StreamingHttpResponse(
        generate(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )
