"""
-----------------------------------------------------------------------------
Archivo: luckfox_client.py
Descripcion: Cliente TCP para comunicacion con el dispositivo Luckfox Pico.
             Genera imagenes de credencial con foto y datos del usuario,
             las envia por socket al puerto 8081, y recibe confirmacion
             de aceptacion o rechazo desde la pantalla tactil.
Fecha de creacion: 15 de Octubre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
import socket
import struct
from PIL import Image
import io

LUCKFOX_IP = '172.32.0.93'
LUCKFOX_PORT = 8081

def send_image_to_luckfox(image_path_or_pil, timeout=30):
    """
    Envía una imagen a la Luckfox para mostrar en pantalla.
    """
    # Cargar o usar imagen PIL
    if isinstance(image_path_or_pil, str):
        img = Image.open(image_path_or_pil)
    else:
        img = image_path_or_pil
    
    # Redimensionar a 480x480 si es necesario
    if img.size != (480, 480):
        img = img.resize((480, 480), Image.BILINEAR)  # Más rápido que LANCZOS
    
    # Convertir a JPEG (calidad reducida para velocidad)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
        
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=70)  # Reducido de 95 a 70
    img_data = img_buffer.getvalue()
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Sin demora
        sock.settimeout(timeout)
        sock.connect((LUCKFOX_IP, LUCKFOX_PORT))
        
        # Enviar tamaño + imagen
        sock.sendall(struct.pack('<I', len(img_data)) + img_data)
        print(f"📤 Imagen enviada ({len(img_data)} bytes)")
        
        # Esperar respuesta
        response = sock.recv(1024).decode('utf-8').strip()
        sock.close()
        
        return "CONFIRM" in response
        
    except socket.timeout:
        print("⏱️ Timeout esperando respuesta")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def generate_credential_image(nombre, rut, carrera, jornada, foto_path=None, foto_base64=None):
    """
    Genera una imagen de credencial 480x480 con diseño INACAP (Fondo Rojo).
    
    Args:
        nombre: Nombre del alumno
        rut: RUT del alumno
        carrera: Carrera del alumno
        jornada: Jornada del alumno
        foto_path: Ruta a foto del alumno (opcional)
        foto_base64: String base64 de la foto (opcional)
    
    Returns:
        PIL Image object
    """
    from PIL import ImageDraw, ImageFont
    import base64
    
    # Colores
    RED_BG = (180, 20, 20) # Rojo INACAP aproximado
    WHITE = (255, 255, 255)
    BOX_BG = (200, 50, 50) # Rojo más claro para la caja de texto
    
    # Crear imagen fondo rojo
    img = Image.new('RGB', (480, 480), color=RED_BG)
    draw = ImageDraw.Draw(img)
    
    try:
        # Usar fuentes del sistema si es posible, sino default
        text_font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        text_font_bold = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Procesar foto
    foto = None
    if foto_base64:
        try:
            if ',' in foto_base64:
                foto_base64 = foto_base64.split(',')[1]
            img_data = base64.b64decode(foto_base64)
            foto = Image.open(io.BytesIO(img_data))
        except Exception as e:
            print(f"Error decodificando base64: {e}")
    elif foto_path:
        try:
            foto = Image.open(foto_path)
        except:
            pass
            
    # Dibujar foto
    foto_size = 180
    foto_x = (480 - foto_size) // 2
    foto_y = 30
    
    # Marco para la foto
    draw.rounded_rectangle([foto_x-5, foto_y-5, foto_x+foto_size+5, foto_y+foto_size+5], 
                          radius=15, fill=WHITE)
    
    if foto:
        # Lógica de recorte agresiva para credenciales antiguas
        w, h = foto.size
        
        # Si es cuadrada (o casi) y tiene resolución suficiente, asumimos que es la credencial generada
        # y recortamos la foto interna.
        aspect_ratio = w / h
        if 0.9 < aspect_ratio < 1.1 and w >= 300:
            # Coordenadas de la foto interna en el diseño de 480x480:
            # x: 140, y: 80, w: 200, h: 200
            # Agregamos un pequeño margen (inset) para evitar bordes
            
            # Escalar coordenadas si la imagen no es exactamente 480
            scale_x = w / 480.0
            scale_y = h / 480.0
            
            left = int(145 * scale_x)
            top = int(85 * scale_y)
            right = int(335 * scale_x)
            bottom = int(275 * scale_y)
            
            foto = foto.crop((left, top, right, bottom))
            
        foto = foto.resize((foto_size, foto_size), Image.LANCZOS)
        mask = Image.new("L", (foto_size, foto_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, foto_size, foto_size], radius=10, fill=255)
        img.paste(foto, (foto_x, foto_y), mask)
    else:
        draw.rounded_rectangle([foto_x, foto_y, foto_x+foto_size, foto_y+foto_size], 
                              radius=10, fill=(200, 200, 200))
        draw.text((240, foto_y + foto_size//2), "Sin Foto", font=text_font, fill=(50,50,50), anchor="mm")
    
    # Caja de datos
    box_x = 40
    box_y = 240
    box_w = 400
    box_h = 140
    draw.rounded_rectangle([box_x, box_y, box_x+box_w, box_y+box_h], radius=15, fill=BOX_BG, outline=WHITE, width=1)
    
    # Texto de datos
    draw.text((240, box_y + 25), nombre, font=text_font_bold, fill=WHITE, anchor="mm")
    draw.text((box_x + 20, box_y + 60), f"RUT: {rut}", font=text_font, fill=WHITE, anchor="lm")
    
    carrera_font = text_font
    if len(carrera) > 25:
        carrera_font = small_font
    draw.text((box_x + 20, box_y + 90), f"Carrera: {carrera}", font=carrera_font, fill=WHITE, anchor="lm")
    
    jornada_texto = "Diurno" if jornada == 'D' else "Vespertina" if jornada == 'V' else jornada
    draw.text((box_x + 20, box_y + 120), f"Jornada: {jornada_texto}", font=text_font, fill=WHITE, anchor="lm")
    
    return img


if __name__ == "__main__":
    # Test
    img = generate_credential_image(
        nombre="Juan Pérez López",
        rut="12.345.678-9",
        carrera="Ingeniería en Informática"
    )
    
    confirmed = send_image_to_luckfox(img)
    
    if confirmed:
        print("✅ Usuario CONFIRMÓ")
    else:
        print("❌ Usuario RECHAZÓ o timeout")
