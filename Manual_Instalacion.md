# Manual de Instalación
## Sistema de Control de Acceso con Reconocimiento Facial - INACAP

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10-yellow.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![Hardware](https://img.shields.io/badge/Hardware-Luckfox%20Pico%20Ultra%20W-orange.svg)

---

Este documento detalla el procedimiento técnico para el despliegue del sistema de reconocimiento facial, incluyendo la configuración del servidor backend (PC Maestro), la base de datos (Firebase) y el dispositivo de borde (Luckfox Pico).

## Índice

1. [Requisitos Previos](#1-requisitos-previos)
2. [Instalación del Servidor (Backend)](#2-instalación-del-servidor-backend)
3. [Configuración de Firebase](#3-configuración-de-firebase)
4. [Despliegue en Luckfox Pico (Edge)](#4-despliegue-en-luckfox-pico-edge)
5. [Ejecución y Verificación](#5-ejecución-y-verificación)
6. [Nuevas Funcionalidades v1.1](#6-nuevas-funcionalidades-v11)
7. [Solución de Problemas](#7-solución-de-problemas)

---

## 1. Requisitos Previos

### 1.1 Hardware

| Componente | Especificación Recomendada | Notas |
|------------|---------------------------|-------|
| **PC Maestro / Servidor** | Intel Core i5, 8GB RAM, Ubuntu 22.04 | Procesa IA y corre Django |
| **Dispositivo de Borde** | Luckfox Pico Ultra W | Ejecuta captura RTSP y UI |
| **Cámara** | Sensor MIS5001 (5MP) | Conexión MIPI CSI a Luckfox |
| **Pantalla** | LCD 4.0" LF40-480x480-ARK | Interfaz SPI/RGB |
| **Red** | Router Wi-Fi dedicado | IP Estática recomendada |

### 1.2 Software Base

- **Sistema Operativo Servidor:** Ubuntu 20.04 LTS
- **Lenguaje:** Python 3.10
- **SDK Biometría:** InspireFace (Librerías compartidas y modelos)
- **Compilador (Luckfox):** Buildroot / SDK Rockchip (si se requiere recompilar C++)

---

## 2. Instalación del Servidor (Backend)

### 2.1 Preparar el Sistema Operativo

Actualizar repositorios e instalar dependencias de sistema necesarias para OpenCV y compilación:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.10 python3.10-venv python3-pip git ffmpeg libgl1-mesa-glx libglib2.0-0 cmake build-essential
```

### 2.2 Clonar el Repositorio

```bash
cd ~
git clone <URL_DEL_REPOSITORIO> Proyecto_RF
cd Proyecto_RF
```

### 2.3 Configurar Entorno Virtual Python

```bash
cd django_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.4 Configurar SDK InspireFace

> **Importante:** El motor de reconocimiento requiere archivos binarios que no se incluyen en el repositorio por tamaño/licencia.

1. Crear carpeta de recursos:

```bash
mkdir -p reconocimiento_facial/core/libs
mkdir -p reconocimiento_facial/core/models
```

2. Copiar `libInspireFace.so` en `core/libs/`.
3. Copiar los archivos de modelos (`.pack`, etc.) en `core/models/`.

---

## 3. Configuración de Firebase

### 3.1 Crear Proyecto y Firestore

1. Ir a [Firebase Console](https://console.firebase.google.com).
2. Crear proyecto: `reconocimiento-facial-inacap`.
3. Ir a **Firestore Database** > **Crear base de datos**.
4. Seleccionar ubicación: `santiago (southamerica-west1)` o `us-central1`.
5. Reglas de seguridad: Configurar temporalmente en modo test o definir reglas de acceso.

### 3.2 Descargar Credenciales de Servicio

1. Ir a **Configuración del proyecto** > **Cuentas de servicio**.
2. Click en **Generar nueva clave privada**.
3. Se descargará un archivo `.json`. Renómbralo a `serviceAccountKey.json`.

### 3.3 Instalar Credenciales en Django

```bash
mkdir -p ~/Proyecto_RF/django_app/firebase_credentials
# Mover el archivo descargado
mv ~/Descargas/serviceAccountKey.json ~/Proyecto_RF/django_app/firebase_credentials/
```

---

## 4. Despliegue en Luckfox Pico (Edge)

El dispositivo Luckfox actúa como **Servidor RTSP** (Video) y **Cliente TCP** (Pantalla).

### 4.1 Conexión de Hardware

- **Cámara:** Conectar cinta MIPI CSI (asegurar orientación de pines).
- **Pantalla:** Conectar pines SPI según diagrama de pines del fabricante.
- **Red:** Conectar cable Ethernet o configurar `wpa_supplicant` para Wi-Fi.

### 4.2 Transferencia de Binarios

Asumiendo que la Luckfox tiene la IP `172.32.0.93` y usuario `root`:

```bash
# Desde el PC Maestro
cd ~/Proyecto_RF/luckfox_firmware/build

# Enviar ejecutable principal
scp Luckfox_RF root@172.32.0.93:/root/

# Enviar recursos de interfaz (imágenes de espera, iconos)
scp assets/*.jpg root@172.32.0.93:/root/
```

### 4.3 Ejecución en el Dispositivo

Conectarse por SSH a la placa:

```bash
ssh root@172.32.0.93
chmod +x /root/Luckfox_RF

# Ejecutar aplicación
./Luckfox_RF
```

**Salida esperada:**
```
RTSP Server started at rtsp://172.32.0.93/live/0
TCP Listening on port 8081
```

---

## 5. Ejecución y Verificación

### 5.1 Iniciar Servidor Django

En el PC Maestro:

```bash
cd ~/Proyecto_RF/django_app
source venv/bin/activate

# Migrar base de datos local (usuarios admin)
python3 manage.py migrate

# Iniciar servidor (asegurar estar en la misma red que la Luckfox)
python3 manage.py runserver 0.0.0.0:8000
```

### 5.2 Checklist de Funcionamiento

| Componente | Acción de Prueba | Resultado Esperado |
|------------|------------------|-------------------|
| **Video** | `ffplay rtsp://172.32.0.93/live/0` | Ventana con video fluido |
| **Conexión Socket** | `nc -zv 172.32.0.93 8081` | `Connection succeeded` |
| **Panel Web** | Navegar a `http://localhost:8000` | Carga el Login / Dashboard |
| **Reconocimiento** | Pararse frente a la cámara | Log: `Face detected: [Nombre]` |

---

## 6. Nuevas Funcionalidades v1.1

### 6.1 Dashboard Estadístico (Business Intelligence)

Se ha integrado un módulo de reportabilidad avanzado en la vista "Lista de Asistencias":

- **Gráfico de Distribución por Carrera:** Visualización circular (Pie Chart) de la asistencia.
- **Gráfico de Asistencia por Rol:** Barras comparativas (Alumnos vs Docentes vs Externos).
- **Librería:** Implementado con `Chart.js` + `chartjs-plugin-datalabels`.

### 6.2 Gestión de Roles (RBAC)

| Rol | Permisos |
|-----|----------|
| **Administrador** | Control total, configuración de sistema y visión de todos los eventos |
| **Encargado de Evento** | Vista restringida solo al evento activo para monitoreo de aforo |

### 6.3 Mejoras de UI/UX

- Indicadores visuales de estado actualizados a paleta de colores corporativa.
- Optimización de la columna "Biometría": Indica estado de vector ("Enrolado/Pendiente") en lugar de datos crudos.

---

## 7. Solución de Problemas

### Error: "Connection Refused" al conectar RTSP

- **Causa:** El binario `Luckfox_RF` no está corriendo en la placa.
- **Solución:** Verificar SSH y ejecutar `./Luckfox_RF`. Asegurar que no hay otro proceso usando la cámara (`rkmedia`).

### Error: "Firebase App Check Token Invalid"

- **Causa:** Reloj del sistema desincronizado.
- **Solución:** Ejecutar `sudo timedatectl set-ntp on` tanto en el servidor como en la Luckfox.

### Error: Detección lenta o nula

- **Causa:** Baja iluminación o distancia incorrecta.
- **Solución:** Encender luz frontal auxiliar. La distancia óptima es entre 40cm y 80cm.

### Pantalla Luckfox en Negro

- **Causa:** Driver de pantalla no inicializado o cable SPI suelto.
- **Solución:** Revisar `dmesg` en Luckfox: `dmesg | grep spi`. Reiniciar placa.

---

**Desarrollado por:** R. Leal & W. Tapia - Ingeniería en Informática 2025.