# Manual Técnico de Uso
## Sistema de Control de Acceso con Reconocimiento Facial - INACAP

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Estado](https://img.shields.io/badge/Estado-Producción-green.svg)
![Rol](https://img.shields.io/badge/Rol-Administrador%2FEncargado-orange.svg)

---

**Fecha de Actualización:** Diciembre 2025  
**Desarrollado por:** R. Leal & W. Tapia

Este documento describe la operación funcional del sistema, desde la gestión administrativa en el panel web hasta la interacción del usuario final con el dispositivo de borde.

---

## Índice

1. [Acceso al Sistema](#1-acceso-al-sistema)
2. [Panel de Control (Dashboard)](#2-panel-de-control-dashboard)
3. [Gestión de Usuarios](#3-gestión-de-usuarios)
4. [Enrolamiento Biométrico](#4-enrolamiento-biométrico)
5. [Gestión de Eventos](#5-gestión-de-eventos)
6. [Operación: Control de Asistencia](#6-operación-control-de-asistencia)
7. [Interacción con Dispositivo de Borde](#7-interacción-con-dispositivo-de-borde)
8. [Reportes y Business Intelligence](#8-reportes-y-business-intelligence)
9. [Solución de Problemas](#9-solución-de-problemas)

---

## 1. Acceso al Sistema

El sistema opera bajo una arquitectura cliente-servidor. El acceso administrativo se realiza vía navegador web desde el PC Maestro o cualquier equipo dentro de la red local autorizada.

### 1.1 Iniciar el Servicio

Antes de acceder, asegúrese de que el servidor Django y el servicio de IA estén activos:

```bash
cd ~/Proyecto_RF/django_app/reconocimiento_facial
source venv/bin/activate
python3 manage.py runserver 0.0.0.0:8000
```

### 1.2 Login y Roles

Acceda a `http://localhost:8000` (o la IP del servidor).

| Rol | Usuario | Alcance | Filtros de Asistencia |
|-----|---------|---------|----------------------|
| **Administrador** | admin | Total (Configuración, Usuarios, Todos los Eventos) | Visibles (Todos) |
| **Encargado** | operador | Limitado (Solo Evento Activo, Validación) | Ocultos (Solo evento actual) |

---

## 2. Panel de Control (Dashboard)

El Dashboard es el centro de mando que ofrece una vista panorámica del estado del sistema en tiempo real.

### Estructura de la Interfaz

```
┌──────────────────────────────────────────────────────────┐
│     INACAP - Sistema de Reconocimiento Facial            │
├──────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐     │
│  │ Usuarios│  │ Eventos │  │Asistencia│  │ Config  │     │
│  │   [12]  │  │   [5]   │  │  [156]   │  │         │     │
│  └─────────┘  └─────────┘  └──────────┘  └─────────┘     │
│                                                          │
│     Métricas de Operación                                │
│  ├── Usuarios registrados: 12 (Total en Firestore)       │
│  ├── Eventos activos: 1 (Requiere atención)              │
│  └── Tasa de Éxito Biométrico: 92%                       │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Gestión de Usuarios

Módulo CRUD para administrar la base de datos de estudiantes, docentes y externos.

### 3.1 Flujo de Creación

1. Navegar a **Menú > Usuarios > Nuevo Usuario**.
2. Completar campos obligatorios: RUT (identificador único), Nombre, Carrera, Jornada.
3. **Estado Biométrico:** Al crear un usuario, este campo aparecerá como "Pendiente" hasta que se realice el enrolamiento.

### 3.2 Edición y Baja

- **Editar:** Permite corregir datos tipográficos. 
  > **Nota:** Si cambia el RUT, deberá volver a enrolar el rostro.
- **Deshabilitar:** Bloquea el acceso sin eliminar los registros históricos de asistencia.

---

## 4. Enrolamiento Biométrico

Este es el proceso crítico donde el motor InspireFace captura y vectoriza el rostro del usuario.

### 4.1 Preparación del Entorno

- **Iluminación:** Asegurar luz frontal uniforme (evitar contraluz).
- **Distancia:** El usuario debe situarse a 50cm de la cámara web del servidor.

### 4.2 Proceso de Captura

1. Seleccionar usuario en la lista y dar click en **"Captura Biométrica"**.
2. El sistema iniciará una ráfaga de captura de **100 frames**.
3. **Validación de Calidad:** El algoritmo seleccionará los frames con mejor alineación y nitidez.
4. **Generación del Vector:** Se calcula un vector promedio de 512 dimensiones y se guarda en Firebase.

```
Progreso de Captura:
65% - Mantenga el rostro firme
```

  **Éxito:** El estado del usuario cambia a "Enrolado" y se muestra la foto de perfil generada.

---

## 5. Gestión de Eventos

Permite planificar las actividades académicas que requieren control de aforo.

### Creación de Eventos

Definir: Título, Expositor, Ubicación y Horario (Inicio/Fin).

### Estados del Evento

| Estado | Significado |
|--------|-------------|
| **Pendiente** | Fecha futura |
| **Activo** | Fecha/Hora actual coincide. Solo los eventos activos permiten marcar asistencia |
| **Finalizado** | Fecha pasada |

---

## 6. Operación: Control de Asistencia

Módulo principal utilizado durante la ejecución del evento. Conecta el stream de video RTSP con el motor de IA.

### 6.1 Panel de Reconocimiento

Al pulsar **"Iniciar Reconocimiento"**, el sistema:

1. Conecta al stream `rtsp://<IP_LUCKFOX>/live/0`.
2. Procesa cada frame buscando coincidencias con la base de datos de vectores (Firestore).
3. **Umbral de Decisión:** Si la similitud (Cosine Similarity) > 0.80, se considera un "Match".

### 6.2 Ingreso Manual (Contingencia)

Si un usuario no logra ser reconocido (por uso de mascarilla, lentes oscuros o fallo del sistema):

1. Click en botón **"Ingreso Manual"**.
2. Digitar RUT.
3. El sistema registra la asistencia marcando el origen como `MANUAL` para estadísticas posteriores.

---

## 7. Interacción con Dispositivo de Borde

Esta sección describe lo que ve el usuario final en la pantalla LCD de la Luckfox Pico.

### 7.1 Flujo de Verificación

Cuando el servidor detecta un rostro, envía una señal TCP al puerto 8081 de la Luckfox, activando la siguiente interfaz:

```
┌─────────────────────────────────────┐
│          CONFIRMAR ACCESO           │
├─────────────────────────────────────┤
│                                     │
│        [ FOTO DEL USUARIO ]         │
│                                     │
│    Juan Pérez López                 │
│    Ingeniería en Informática        │
│                                     │
├──────────────────┬──────────────────┤
│     RECHAZAR     │    ACEPTAR       │
└──────────────────┴──────────────────┘
```

### 7.2 Acciones del Usuario

| Botón | Acción | Resultado |
|-------|--------|-----------|
| **ACEPTAR** | El usuario confirma que los datos son correctos | Asistencia guardada, pantalla muestra borde VERDE |
| **RECHAZAR** | El usuario indica error | No se guarda asistencia, pantalla muestra borde ROJO |

**Tiempo de Espera:** 30 segundos. Si no hay interacción, se descarta.

---

## 8. Reportes y Business Intelligence

**Novedad v1.1:** Visualización gráfica de datos utilizando la librería Chart.js.

### 8.1 Dashboard Estadístico

Ubicado en la pestaña "Lista de Asistencias", ofrece:

- **Gráfico de Torta (Carreras):** Distribución porcentual de asistencia (Ej: 40% Informática, 30% Mecánica).
- **Gráfico de Barras (Roles):** Comparativa de asistencia (Alumnos vs. Docentes vs. Externos).
- **Indicadores de Eventos:** Badges con nombres de eventos incluidos en las estadísticas.

### 8.2 Exportación de Datos

Para fines administrativos, los listados pueden exportarse:

1. Seleccionar Evento.
2. Click en botón **"Exportar a Excel"**.
3. El archivo generado incluye: Nombre, RUT, Hora Exacta, Método de Entrada (Bio/Manual) y Nivel de Confianza.

---

## 9. Solución de Problemas

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| Video en negro | Luckfox no transmite RTSP | Reiniciar placa Luckfox y verificar conexión de red |
| No reconoce rostros | Luz insuficiente | Encender luz auxiliar frontal. Acercar usuario a 50cm |
| Pantalla Luckfox no responde | Servicio TCP caído | Verificar que `Luckfox_RF` esté corriendo en la placa |
| Error de Base de Datos | Sin internet | El sistema requiere conexión para validar con Firebase |

---

**Soporte Técnico:** Contactar al equipo de desarrollo (R. Leal / W. Tapia).