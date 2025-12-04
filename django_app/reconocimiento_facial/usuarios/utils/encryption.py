"""Utilidades de encriptación para imágenes usando Fernet."""

from cryptography.fernet import Fernet


def generar_clave():
    """Genera una clave de encriptación Fernet y la guarda."""
    clave = Fernet.generate_key()
    with open("media/encryption_key.key", "wb") as key_file:
        key_file.write(clave)


def cargar_clave():
    """Carga la clave de encriptación desde el archivo."""
    with open("media/encryption_key.key", "rb") as key_file:
        return key_file.read()


def encriptar_imagen(path_imagen):
    """
    Encripta un archivo de imagen usando Fernet.
    
    Args:
        path_imagen: Ruta absoluta al archivo de imagen
    """
    clave = cargar_clave()
    fernet = Fernet(clave)
    with open(path_imagen, "rb") as file:
        datos = file.read()
    datos_encriptados = fernet.encrypt(datos)
    with open(path_imagen, "wb") as file:
        file.write(datos_encriptados)


def desencriptar_imagen(path_imagen):
    """
    Desencripta un archivo de imagen usando Fernet.
    
    Args:
        path_imagen: Ruta absoluta al archivo de imagen encriptado
    """
    clave = cargar_clave()
    fernet = Fernet(clave)
    with open(path_imagen, "rb") as file:
        datos_encriptados = file.read()
    datos_desencriptados = fernet.decrypt(datos_encriptados)
    with open(path_imagen, "wb") as file:
        file.write(datos_desencriptados)
