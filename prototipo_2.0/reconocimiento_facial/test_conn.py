from usuarios.services.luckfox_client import generate_credential_image, send_image_to_luckfox
import base64
import time
import sys

print('Generando imagen de prueba...', flush=True)
try:
    img = generate_credential_image('Test User', '1-9', 'Test', 'D')
    print('Imagen generada.', flush=True)

    print('Intentando conectar a 172.32.0.93:8081...', flush=True)
    start_time = time.time()
    confirmed = send_image_to_luckfox(img, timeout=5)
    end_time = time.time()

    print(f'Resultado: {confirmed}', flush=True)
    print(f'Tiempo: {end_time - start_time:.2f}s', flush=True)
except Exception as e:
    print(f'ERROR: {e}', flush=True)
