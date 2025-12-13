# **MANUAL TÉCNICO DE USO**
# **Sistema de Reconocimiento Facial INACAP**

---

**Versión:** 1.0  
**Fecha:** Diciembre 2024

---

## **ÍNDICE**

1. [Acceso al Sistema](#1-acceso-al-sistema)
2. [Panel de Control (Dashboard)](#2-panel-de-control-dashboard)
3. [Gestión de Usuarios](#3-gestión-de-usuarios)
4. [Registro Biométrico](#4-registro-biométrico)
5. [Gestión de Eventos](#5-gestión-de-eventos)
6. [Control de Asistencia](#6-control-de-asistencia)
7. [Reconocimiento Facial en Vivo](#7-reconocimiento-facial-en-vivo)
8. [Reportes y Estadísticas](#8-reportes-y-estadísticas)

---

## **1. ACCESO AL SISTEMA**

### 1.1 Iniciar el Servidor

```bash
cd ~/Proyecto_RF/django_app/reconocimiento_facial
source venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

### 1.2 Acceder al Dashboard

1. Abrir navegador web (Chrome/Firefox recomendado)
2. Ir a: `http://IP_SERVIDOR:8000`
3. Ingresar credenciales de administrador

### 1.3 Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **Administrador** | Acceso completo a todas las funciones |
| **Encargado** | Gestión de eventos y control de asistencia |

---

## **2. PANEL DE CONTROL (DASHBOARD)**

### 2.1 Elementos del Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  🏠 INACAP - Sistema de Reconocimiento Facial           │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Usuarios│  │ Eventos │  │Asistencia│  │ Config  │    │
│  │   [12]  │  │   [5]   │  │  [156]  │  │   [⚙️]  │    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│                                                         │
│  📊 Estadísticas Rápidas                                │
│  ├── Usuarios registrados: 12                           │
│  ├── Eventos activos: 2                                 │
│  └── Asistencias hoy: 45                                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Navegación Principal

| Sección | Función |
|---------|---------|
| **Usuarios** | Listar, crear, editar usuarios |
| **Registro Biométrico** | Capturar datos faciales |
| **Eventos** | Gestionar eventos/actividades |
| **Reconocimiento** | Control de asistencia en vivo |

---

## **3. GESTIÓN DE USUARIOS**

### 3.1 Listar Usuarios

1. Click en **"Usuarios"** en el menú
2. Vista de tabla con todos los usuarios registrados
3. Filtros disponibles:
   - Por jornada (Diurna/Vespertina)
   - Por estado (Activo/Inactivo)
   - Por carrera

### 3.2 Crear Usuario Nuevo

1. Click en **"Nuevo Usuario"**
2. Completar formulario:
   - **RUT:** Formato 12345678-9
   - **Nombre Completo:** Nombres y apellidos
   - **Carrera:** Seleccionar de lista
   - **Jornada:** Diurna o Vespertina
3. Click en **"Guardar"**

> ⚠️ **Nota:** El usuario debe completar el registro biométrico posteriormente.

### 3.3 Editar Usuario

1. En la lista, click en **"Editar"** (ícono lápiz)
2. Modificar campos necesarios
3. Click en **"Actualizar"**

### 3.4 Deshabilitar Usuario

1. Click en **"Deshabilitar"** (ícono candado)
2. Confirmar acción
3. El usuario no podrá ser reconocido hasta reactivarlo

---

## **4. REGISTRO BIOMÉTRICO**

### 4.1 Requisitos Previos

- Cámara IP conectada y funcionando
- Buena iluminación frontal
- Usuario mirando directamente a la cámara

### 4.2 Proceso de Registro

1. Ir a **"Registro Biométrico"**
2. Ingresar RUT del usuario
3. Verificar datos mostrados
4. Click en **"Iniciar Captura"**

### 4.3 Durante la Captura

```
┌─────────────────────────────────────────┐
│        📷 CAPTURA EN PROGRESO           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │                                 │   │
│  │      [Vista de cámara]          │   │
│  │                                 │   │
│  │         😊                      │   │
│  │                                 │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Progreso: ████████░░ 80%              │
│  Frames capturados: 40/50               │
│                                         │
│  ⏱️ Tiempo restante: 2 segundos         │
└─────────────────────────────────────────┘
```

**Instrucciones para el usuario:**
- Mantener rostro centrado
- Mirar directamente a la cámara
- No moverse durante la captura
- Mantener expresión neutral

### 4.4 Confirmación de Registro

Una vez completada la captura:
- Se extraen 50 vectores faciales
- Se calcula el vector promedio
- Se guarda foto de perfil
- Mensaje: "✅ Registro biométrico completado"

---

## **5. GESTIÓN DE EVENTOS**

### 5.1 Crear Evento

1. Ir a **"Eventos"** → **"Nuevo Evento"**
2. Completar información:
   - **Nombre:** Título del evento
   - **Descripción:** Detalles adicionales
   - **Fecha:** YYYY-MM-DD
   - **Hora inicio:** HH:MM
   - **Hora fin:** HH:MM
   - **Relator:** Nombre del expositor
   - **Ubicación:** Sala/Auditorio

### 5.2 Estados del Evento

| Estado | Significado |
|--------|-------------|
| 🟡 **Pendiente** | Aún no ha comenzado |
| 🟢 **Activo** | En curso (hora actual dentro del rango) |
| ⚫ **Finalizado** | Ya terminó |

### 5.3 Editar/Eliminar Evento

- **Editar:** Click en ✏️ para modificar datos
- **Eliminar:** Click en 🗑️ (solo si no tiene asistencias)

---

## **6. CONTROL DE ASISTENCIA**

### 6.1 Iniciar Control de Asistencia

1. En la lista de eventos, click en **"Reconocer"**
2. Se abre la pantalla de reconocimiento facial

### 6.2 Pantalla de Reconocimiento

```
┌────────────────────────────────────────────────────────────┐
│  📹 RECONOCIMIENTO FACIAL - Evento: Charla TI             │
├──────────────────────────────────┬─────────────────────────┤
│                                  │  📊 ASISTENTES          │
│  ┌──────────────────────────┐   │  ┌───────────────────┐  │
│  │                          │   │  │ Total:    [45]    │  │
│  │    [Stream de cámara]    │   │  │ Biométrico: [38]  │  │
│  │                          │   │  │ Manual:   [7]     │  │
│  │                          │   │  └───────────────────┘  │
│  └──────────────────────────┘   │                         │
│                                  │  👤 ÚLTIMO RECONOCIDO   │
│  [▶️ Iniciar] [⏹️ Detener]       │  ┌───────────────────┐  │
│  [📝 Ingreso Manual]             │  │ Juan Pérez        │  │
│                                  │  │ RUT: 12345678-9   │  │
│                                  │  │ ✅ Registrado     │  │
│                                  │  └───────────────────┘  │
└──────────────────────────────────┴─────────────────────────┘
```

### 6.3 Flujo de Reconocimiento

1. Click en **"Iniciar Reconocimiento"**
2. Sistema busca rostros continuamente
3. Al detectar match:
   - Envía credencial a Luckfox
   - Usuario confirma en pantalla táctil
   - Se registra asistencia
4. Dashboard se actualiza automáticamente

### 6.4 Ingreso Manual

Para usuarios sin registro biométrico:
1. Click en **"Ingreso Manual"**
2. Ingresar RUT (se autocompletan datos si existe)
3. Completar campos requeridos
4. Click en **"Registrar Asistencia"**

---

## **7. RECONOCIMIENTO FACIAL EN VIVO**

### 7.1 Flujo de Confirmación en Luckfox

```
┌─────────────────────────────────────┐
│          LUCKFOX PICO               │
│                                     │
│  ┌─────────────────────────────┐   │
│  │       📷 [Foto]             │   │
│  │                             │   │
│  │     Juan Pérez López        │   │
│  │     RUT: 12.345.678-9       │   │
│  │     Ing. Informática        │   │
│  │     Jornada: Diurna         │   │
│  │                             │   │
│  │   [❌ NO]      [✅ SÍ]      │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 7.2 Acciones del Usuario

| Botón | Acción | Resultado |
|-------|--------|-----------|
| ✅ **SÍ** | Confirmar identidad | Se registra asistencia |
| ❌ **NO** | Rechazar identidad | Se cancela, vuelve a buscar |

### 7.3 Timeout de Confirmación

- Tiempo límite: **30 segundos**
- Si no hay acción: Se considera rechazo
- Sistema continúa buscando otros rostros

---

## **8. REPORTES Y ESTADÍSTICAS**

### 8.1 Ver Asistencias de un Evento

1. Ir a **"Eventos"**
2. Click en **"Ver Asistencias"**
3. Tabla con:
   - Nombre del asistente
   - RUT
   - Hora de registro
   - Método (biométrico/manual)
   - Similitud (si aplica)

### 8.2 Exportar Datos

*(Funcionalidad futura)*

- Exportar a CSV
- Exportar a PDF
- Enviar por correo

### 8.3 Estadísticas del Dashboard

| Métrica | Descripción |
|---------|-------------|
| **Total Usuarios** | Cantidad de usuarios registrados |
| **Con Biometría** | Usuarios con vector facial |
| **Eventos Activos** | Eventos en curso hoy |
| **Asistencias Hoy** | Registros del día actual |

---

## **ATAJOS DE TECLADO**

| Tecla | Acción |
|-------|--------|
| `Ctrl + N` | Nuevo usuario |
| `Ctrl + E` | Nuevo evento |
| `Esc` | Cerrar modal |
| `Enter` | Confirmar formulario |

---

## **GLOSARIO**

| Término | Definición |
|---------|------------|
| **Vector Facial** | Representación numérica de 512 valores que describe características únicas del rostro |
| **Similitud** | Porcentaje de coincidencia entre dos vectores (0-100%) |
| **Umbral** | Mínima similitud requerida para confirmar identidad (45% por defecto) |
| **RTSP** | Protocolo de streaming de video en tiempo real |
| **Match** | Coincidencia exitosa entre rostro capturado y usuario registrado |

---

## **CONTACTO SOPORTE**

Para asistencia técnica:
- Revisar logs del servidor Django
- Consultar Manual de Instalación
- Revisar Informe Técnico completo

---

**Documento generado - Diciembre 2024**
