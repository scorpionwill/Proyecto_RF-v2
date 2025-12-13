"""Vistas para reconocimiento facial en Django"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import cv2
import numpy as np
from ..services.firebase_service import firebase_service
from ..services.matching_service import encontrar_match
from ..services.inspireface_service import inspireface_service
from ..decorators import encargado_or_admin

# Configuración RTSP
RTSP_URL_HIGH = "rtsp://172.32.0.93/live/0"
RTSP_URL_LOW = "rtsp://172.32.0.93/live/1"


def entrenar_modelo(request):
    """Entrenar el modelo de reconocimiento facial"""
    messages.info(request, "Esta funcionalidad ya no es necesaria. El reconocimiento se hace por vectores.")
    return redirect('pagina_inicio')


@encargado_or_admin
def reconocer_usuario(request, evento_id):
    """Página de reconocimiento en vivo para un evento"""
    evento = firebase_service.obtener_evento(evento_id)
    
    if not evento:
        messages.error(request, "Evento no encontrado")
        return redirect('listar_eventos')
    
    # Obtener estadísticas de asistencia para este evento
    asistencias = firebase_service.listar_asistencias(id_evento=evento_id)
    total_asistentes = len(asistencias) if asistencias else 0
    
    # Contar por método
    biometricos = sum(1 for a in asistencias if a.get('metodo') == 'biometrico') if asistencias else 0
    manuales = total_asistentes - biometricos
    
    context = {
        'evento': evento,
        'evento_id': evento_id,
        'total_asistentes': total_asistentes,
        'biometricos': biometricos,
        'manuales': manuales
    }
    return render(request, 'reconocimiento_facial.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@encargado_or_admin
def capturar_y_reconocer(request):
    """
    Captura frames del RTSP, detecta rostro y busca match con criterio de persistencia.
    Criterio: Intentar hasta 5 veces, si 2 veces coincide el mismo usuario, se confirma.
    """
    evento_id = request.POST.get('evento_id')
    solo_detectar = request.POST.get('solo_detectar', 'false').lower() == 'true'
    verificar_rut = request.POST.get('verificar_rut')
    
    print(f"\n{'='*60}")
    print(f"🎯 NUEVA CAPTURA - Evento: {evento_id}")
    print(f"   Modo: {'SOLO_DETECTAR' if solo_detectar else 'VERIFICACIÓN' if verificar_rut else 'AUTO'}")
    print(f"{'='*60}")
    
    if not evento_id:
        return JsonResponse({'error': 'evento_id requerido'}, status=400)
    
    evento = firebase_service.obtener_evento(evento_id)
    if not evento:
        return JsonResponse({'error': 'Evento no encontrado'}, status=404)
    
    try:
        # 1. Pre-cargar usuarios para eficiencia (evitar consultas repetidas en el loop)
        usuarios_db = firebase_service.listar_usuarios()
        
        # 2. Configuración del ciclo de reconocimiento con timeout
        import time
        TIMEOUT_SEGUNDOS = 2.0  # Tiempo máximo por ciclo de búsqueda
        
        mejor_resultado_global = None
        match_confirmado = None
        
        print(f"🔄 Iniciando búsqueda continua (timeout: {TIMEOUT_SEGUNDOS}s)")
        
        cap = cv2.VideoCapture(RTSP_URL_HIGH, cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if not cap.isOpened():
            return JsonResponse({'success': False, 'error': 'No se pudo conectar al stream RTSP'}, status=500)
        
        try:
            # Sincronizar buffer (mínimo)
            cap.read()
            
            tiempo_inicio = time.time()
            intento = 0
            
            # Loop continuo con timeout en lugar de intentos fijos
            while (time.time() - tiempo_inicio) < TIMEOUT_SEGUNDOS:
                # Intentar capturar y procesar un frame
                ret, frame_temp = cap.read()
                if not ret: 
                    continue
                
                # Redimensionar a Full HD 1080p para consistencia y velocidad
                frame_temp = cv2.resize(frame_temp, (1920, 1080), interpolation=cv2.INTER_LINEAR)
                
                # DEBUG: Confirmar resolución
                if intento == 0:
                    print(f"📏 Resolución de análisis: {frame_temp.shape[1]}x{frame_temp.shape[0]}")
                
                frame = None
                
                # InspireFace detection + embedding
                # Usamos BGR directo para coincidir con el formato de registro (luckfox_views.py)
                vector_actual = inspireface_service.get_face_embedding(frame_temp)
                
                if vector_actual:
                    frame = frame_temp
            
                if frame is None:
                    print(f"  ⚠️ Intento {intento+1}: No se detectó rostro (InspireFace)")
                    intento += 1
                    continue
                
                # Buscar match
                # Usamos umbral 0.45 para ser más permisivo
                resultado = encontrar_match(vector_actual, umbral_similitud=0.45, usuarios_cache=usuarios_db)
                
                if resultado.match:
                    rut = resultado.usuario['rut']
                    
                    print(f"  ✅ Intento {intento+1}: Match con {resultado.usuario['nombre']} (Similitud: {resultado.similitud:.2f})")
                    
                    # Actualizar mejor resultado global
                    if mejor_resultado_global is None or resultado.similitud > mejor_resultado_global.similitud:
                        mejor_resultado_global = resultado
                    
                    # CRITERIO SINGLE SHOT: Si supera el 50%, confirmamos inmediatamente
                    print(f"🎉 CONFIRMADO: {resultado.usuario['nombre']} (Similitud > 50%)")
                    match_confirmado = resultado
                    break
                else:
                    print(f"  ❌ Intento {intento+1}: Sin match (Mejor: {resultado.similitud:.2f})")
                    if mejor_resultado_global is None or resultado.similitud > mejor_resultado_global.similitud:
                        mejor_resultado_global = resultado
                
                intento += 1
                        
        finally:
            cap.release()
            
        # 3. Procesar resultado final
        resultado_final = match_confirmado if match_confirmado else mejor_resultado_global
        
        if not resultado_final:
             return JsonResponse({'success': False, 'no_face': True, 'message': 'No se pudo detectar rostro en los intentos realizados'})

        mejor_match = resultado_final.usuario if resultado_final.match else (resultado_final.usuario if resultado_final.usuario else None)
        mejor_similitud = resultado_final.similitud
        umbral = 0.50
        
        # Lógica de respuesta (similar a la original pero usando resultado_final)
        if match_confirmado:
            print(f"✅ MATCH FINAL CONFIRMADO: {mejor_match['nombre']}")
            
            if verificar_rut:
                if mejor_match['rut'] == verificar_rut:
                    return JsonResponse({
                        'success': True, 'match': True,
                        'usuario': mejor_match,
                        'similitud': float(mejor_similitud)
                    })
                else:
                    return JsonResponse({'success': False, 'match': False, 'message': 'No coincide con el usuario esperado'})
            
            # if solo_detectar:
            #     return JsonResponse({
            #         'success': True, 'match': True,
            #         'usuario': mejor_match,
            #         'similitud': float(mejor_similitud),
            #         'umbral': umbral
            #     })
            
            # CONFIRMACIÓN EN LUCKFOX
            from ..services.luckfox_client import generate_credential_image, send_image_to_luckfox
            
            print(f"🖥️ Solicitando confirmación en Luckfox para: {mejor_match['nombre']}")
            
            # Generar imagen de credencial
            credencial_img = generate_credential_image(
                nombre=mejor_match['nombre'],
                rut=mejor_match['rut'],
                carrera=mejor_match.get('carrera', 'N/A'),
                jornada=mejor_match.get('jornada', 'D'),
                foto_base64=mejor_match.get('imagen')
            )
            
            # Enviar y esperar confirmación
            confirmado = send_image_to_luckfox(credencial_img)
            
            if not confirmado:
                print(f"❌ Usuario rechazó confirmación en pantalla Luckfox")
                return JsonResponse({
                    'success': False, 
                    'match': True, 
                    'usuario': mejor_match,
                    'message': 'Usuario rechazó la confirmación en el dispositivo'
                })
            
            print(f"✅ Usuario confirmó en pantalla Luckfox")

            # Registrar asistencia
            try:
                asistencia_id = firebase_service.registrar_asistencia(
                    id_evento=evento_id,
                    rut_usuario=mejor_match['rut'],
                    metodo='biometrico',
                    similitud=float(mejor_similitud)
                )
                return JsonResponse({
                    'success': True, 'match': True,
                    'asistencia': 'registrada' if asistencia_id.get('status') == 'registrada' else 'existe',
                    'usuario': mejor_match,
                    'similitud': float(mejor_similitud)
                })
            except Exception as e:
                print(f"⚠️ Error registrando asistencia: {e}")
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
                
        else:
            # No hubo match confirmado (o no hubo match en absoluto)
            nombre_candidato = mejor_match['nombre'] if mejor_match else "Desconocido"
            print(f"❌ SIN MATCH CONFIRMADO. Mejor candidato: {nombre_candidato} ({mejor_similitud*100:.1f}%)")
            
            return JsonResponse({
                'success': True,
                'match': False,
                'similitud_maxima': float(mejor_similitud),
                'mejor_nombre': nombre_candidato,
                'umbral': umbral,
                'message': 'No se encontró un match suficientemente confiable'
            })

    except Exception as e:
        print(f"❌ ERROR EN RECONOCIMIENTO: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@encargado_or_admin
def confirmar_asistencia(request):
    """Registra asistencia después de confirmación del usuario."""
    evento_id = request.POST.get('evento_id')
    rut = request.POST.get('rut')
    
    if not evento_id or not rut:
        return JsonResponse({'success': False, 'error': 'evento_id y rut son requeridos'}, status=400)
    
    try:
        evento = firebase_service.obtener_evento(evento_id)
        if not evento:
            return JsonResponse({'success': False, 'error': 'Evento no encontrado'}, status=404)
        
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        if not usuario:
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)
        
        asistencia_id = firebase_service.registrar_asistencia(
            id_evento=evento_id,
            rut_usuario=rut
        )
        
        print(f"✅ Asistencia confirmada y registrada: {usuario['nombre']} → {asistencia_id}")
        
        return JsonResponse({
            'success': True,
            'asistencia': 'registrada',
            'asistencia_id': asistencia_id,
            'mensaje': f'Asistencia registrada para {usuario["nombre"]}'
        })
        
    except Exception as e:
        if 'ya está registrado' in str(e).lower():
            print(f"ℹ️ Usuario ya registrado en este evento")
            return JsonResponse({'success': True, 'asistencia': 'existe', 'mensaje': 'Este usuario ya está registrado en el evento'})
        else:
            print(f"❌ Error registrando asistencia: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@encargado_or_admin
def registrar_asistencia_manual(request):
    """
    Registra asistencia manual de un usuario.
    Si el usuario no existe, lo crea sin datos biométricos.
    """
    evento_id = request.POST.get('evento_id')
    rut = request.POST.get('rut')
    nombre = request.POST.get('nombre')
    carrera = request.POST.get('carrera')
    jornada = request.POST.get('jornada', 'D')
    
    if not all([evento_id, rut, nombre, carrera, jornada]):
        return JsonResponse({
            'success': False,
            'error': 'Todos los campos son requeridos'
        }, status=400)
    
    try:
        # Verificar que el evento existe
        evento = firebase_service.obtener_evento(evento_id)
        if not evento:
            return JsonResponse({
                'success': False,
                'error': 'Evento no encontrado'
            }, status=404)
        
        # Buscar si el usuario existe
        usuario = firebase_service.obtener_usuario_por_rut(rut)
        
        if not usuario:
            # Crear usuario sin vector facial (registro manual)
            print(f"📝 Creando usuario temporal para registro manual: {nombre}")
            try:
                # Obtener imagen por defecto
                from ..services.firebase_service import get_default_profile_image
                default_image = get_default_profile_image()
                
                firebase_service.crear_usuario(
                    nombre=nombre,
                    rut=rut,
                    carrera=carrera,
                    jornada=jornada,
                    imagen_base64=default_image,  # Usar imagen por defecto
                    vector_facial=None
                )
                print(f"✅ Usuario creado con imagen por defecto: {nombre}")
            except Exception as e:
                print(f"⚠️ Error creando usuario (puede ya existir): {e}")
        
        # Registrar asistencia con método manual
        resultado = firebase_service.registrar_asistencia(
            id_evento=evento_id,
            rut_usuario=rut,
            metodo='manual',
            similitud=None
        )
        
        if resultado.get('status') == 'registrada':
            print(f"✅ Asistencia manual registrada: {nombre}")
            return JsonResponse({
                'success': True,
                'asistencia': 'registrada',
                'mensaje': f'Asistencia registrada para {nombre}'
            })
        elif resultado.get('status') == 'existe':
            print(f"ℹ️ Asistencia ya existe para: {nombre}")
            return JsonResponse({
                'success': True,
                'asistencia': 'existe',
                'mensaje': f'{nombre} ya tiene asistencia registrada en este evento'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Error desconocido al registrar asistencia'
            }, status=500)
            
    except Exception as e:
        print(f"❌ Error en registro manual: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
