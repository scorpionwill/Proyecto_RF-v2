# **MANUAL DE INSTALACIÓN**
# **Sistema de Reconocimiento Facial INACAP**

---

**Versión:** 1.0  
**Fecha:** Diciembre 2024

---

## **ÍNDICE**

1. [Requisitos Previos](#1-requisitos-previos)
2. [Instalación del Servidor](#2-instalación-del-servidor)
3. [Configuración de Firebase](#3-configuración-de-firebase)
4. [Configuración de la Cámara IP](#4-configuración-de-la-cámara-ip)
5. [Despliegue en Luckfox Pico](#5-despliegue-en-luckfox-pico)
6. [Verificación de la Instalación](#6-verificación-de-la-instalación)
7. [Solución de Problemas](#7-solución-de-problemas)

---

## **1. REQUISITOS PREVIOS**

### 1.1 Hardware Requerido

| Componente | Especificación Mínima |
|------------|----------------------|
| PC/Servidor | Intel Core i5, 4GB RAM, 10GB SSD |
| Cámara IP | Soporte RTSP, 720p mínimo |
| Luckfox Pico | Con pantalla LCD y panel táctil |
| Red | Switch/Router con puertos libres |
| Cables | Ethernet Cat5e o superior |

### 1.2 Software Requerido

- **Sistema Operativo:** Ubuntu 20.04 LTS o superior
- **Python:** 3.10 o superior
- **Git:** Para clonar el repositorio

---

## **2. INSTALACIÓN DEL SERVIDOR**

### 2.1 Actualizar el Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.2 Instalar Dependencias del Sistema

```bash
sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    git \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-dejavu-core
```

### 2.3 Clonar el Proyecto

```bash
cd ~
git clone <URL_DEL_REPOSITORIO> Proyecto_RF
cd Proyecto_RF
```

> **Nota:** Si tienes el proyecto comprimido:
> ```bash
> tar -xzf Proyecto_RF.tar.gz
> ```

### 2.4 Crear Entorno Virtual

```bash
cd django_app/reconocimiento_facial
python3 -m venv venv
source venv/bin/activate
```

### 2.5 Instalar Dependencias Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.6 Verificar InspireFace

```bash
python3 -c "import inspireface; print('InspireFace OK')"
```

---

## **3. CONFIGURACIÓN DE FIREBASE**

### 3.1 Crear Proyecto en Firebase

1. Ir a [Firebase Console](https://console.firebase.google.com)
2. Click en **"Agregar proyecto"**
3. Nombre: `reconocimiento-facial-inacap`
4. Click en **"Crear proyecto"**

### 3.2 Habilitar Firestore Database

1. Menú lateral → **"Firestore Database"**
2. Click en **"Crear base de datos"**
3. Seleccionar **"Modo de producción"**
4. Elegir ubicación: `us-central1`

### 3.3 Generar Credenciales

1. Ir a **Configuración del proyecto** (⚙️)
2. Pestaña **"Cuentas de servicio"**
3. Click en **"Generar nueva clave privada"**
4. Guardar el archivo JSON

### 3.4 Instalar Credenciales

```bash
mkdir -p ~/Proyecto_RF/django_app/firebase_credentials
cp ~/Descargas/tu-proyecto-firebase-adminsdk-xxxxx.json \
   ~/Proyecto_RF/django_app/firebase_credentials/serviceAccountKey.json
```

---

## **4. CONFIGURACIÓN DE LA CÁMARA IP**

### 4.1 Configurar IP Estática

En la interfaz web de la cámara:
- **IP:** 172.32.0.93
- **Máscara:** 255.255.255.0
- **Gateway:** 172.32.0.1

### 4.2 Habilitar Stream RTSP

- **Stream principal:** `rtsp://172.32.0.93/live/0` (1080p)
- **Stream secundario:** `rtsp://172.32.0.93/live/1` (720p)

### 4.3 Verificar Conectividad

```bash
ping -c 3 172.32.0.93
ffplay rtsp://172.32.0.93/live/0
```

---

## **5. DESPLIEGUE EN LUCKFOX PICO**

### 5.1 Conexión Física

1. Conectar pantalla LCD al puerto SPI
2. Conectar panel táctil al puerto I2C
3. Conectar cable Ethernet
4. Conectar alimentación USB-C

### 5.2 Transferir Archivos

```bash
cd ~/luckfox_ui_rebuild
scp Luckfox_RF root@172.32.0.93:/root/
scp *.jpg root@172.32.0.93:/root/
```

### 5.3 Configurar y Ejecutar

```bash
ssh root@172.32.0.93
chmod +x /root/Luckfox_RF
./Luckfox_RF
```

Salida esperada:
```
=== Luckfox UI Start ===
Server ready on port 8081
```

---

## **6. VERIFICACIÓN DE LA INSTALACIÓN**

### 6.1 Iniciar el Servidor

```bash
cd ~/Proyecto_RF/django_app/reconocimiento_facial
source venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

### 6.2 Checklist de Verificación

| Componente | Prueba | Esperado |
|------------|--------|----------|
| Firebase | Ver logs | "✓ Firebase inicializado" |
| Cámara | `ping 172.32.0.93` | Respuesta OK |
| Luckfox | `nc -zv 172.32.0.93 8081` | "Connection succeeded" |
| Web | http://localhost:8000 | Dashboard visible |

---

## **7. SOLUCIÓN DE PROBLEMAS**

### Error: "No se encontró serviceAccountKey.json"
```bash
ls -la ~/Proyecto_RF/django_app/firebase_credentials/
# Verificar que existe el archivo
```

### Error: "No se pudo conectar al stream RTSP"
```bash
ping 172.32.0.93
ffplay rtsp://172.32.0.93/live/0
```

### Error: "Timeout esperando respuesta" (Luckfox)
```bash
ssh root@172.32.0.93
ps aux | grep Luckfox
./Luckfox_RF  # Si no está corriendo
```

### Error: "Permission denied" en Luckfox
```bash
chmod +x /root/Luckfox_RF
```

### Error: "0 faces detected"
- Mejorar iluminación frontal
- Centrar rostro en cámara
- Acercarse a la cámara

---

**Documento generado - Diciembre 2024**
