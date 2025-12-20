"""
-----------------------------------------------------------------------------
Archivo: firebase_service.py
Descripcion: Servicio de conexion y operaciones con Firebase Firestore.
             Implementa CRUD de usuarios, gestion de eventos, registro
             de asistencias, y almacenamiento de vectores faciales.
             Reemplaza MySQL/Django ORM con base de datos NoSQL en la nube.
Fecha de creacion: 15 de Septiembre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import base64
import os


def get_default_profile_image():
    """Retorna la imagen de perfil por defecto en base64."""
    try:
        # Ruta a la imagen por defecto
        default_image_path = os.path.join(
            os.path.dirname(__file__),
            '../static/img/default_profile.png'
        )
        
        if os.path.exists(default_image_path):
            with open(default_image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                return f"data:image/png;base64,{img_data}"
        return None
    except Exception as e:
        print(f"Error cargando imagen por defecto: {e}")
        return None


class FirebaseService:
    """Singleton para manejar conexión y operaciones con Firebase"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.initialize()
            FirebaseService._initialized = True
    
    def initialize(self):
        """Inicializa Firebase Admin SDK"""
        try:
            # Buscar archivo de credenciales
            cred_paths = [
                os.path.join(os.path.dirname(__file__), '../../../firebase_credentials/serviceAccountKey.json'),
                os.path.expanduser('~/Proyecto_RF/django_app/firebase_credentials/serviceAccountKey.json'),
                '/home/scorpionwill/Proyecto_RF/django_app/firebase_credentials/serviceAccountKey.json',
            ]
            
            cred_path = None
            for path in cred_paths:
                if os.path.exists(path):
                    cred_path = path
                    break
            
            if not cred_path:
                raise FileNotFoundError(
                    "No se encontró serviceAccountKey.json. "
                    "Colócalo en Proyecto_RF/django_app/firebase_credentials/"
                )
            
            # Inicializar Firebase
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            print("✓ Firebase inicializado correctamente")
            
        except ValueError:
            # Ya está inicializado
            self.db = firestore.client()
        except Exception as e:
            print(f"✗ Error inicializando Firebase: {e}")
            raise
    
    def crear_usuario(self, nombre, rut, carrera, jornada='D', imagen_base64=None, vector_facial=None):
        """
        Crea un nuevo usuario en Firestore (versión simple, 1 vector).
        
        Args:
            nombre (str): Nombre completo
            rut (str): RUT único
            carrera (str): Carrera del alumno
            jornada (str): 'D' (Diurna) o 'V' (Vespertina)
            imagen_base64 (str): Imagen en base64 (opcional)
            vector_facial (list): Lista de 512 floats (opcional)
        
        Returns:
            dict: Usuario creado con ID
        """
        try:
            # Verificar si ya existe
            if self.obtener_usuario_por_rut(rut):
                raise ValueError(f"Ya existe un usuario con RUT {rut}")
            
            usuario_data = {
                'nombre': nombre,
                'rut': rut,
                'carrera': carrera,
                'jornada': jornada,
                'imagen': imagen_base64,
                'vector_facial': vector_facial,
                'fecha_registro': datetime.now().isoformat(),
                'activo': True
            }
            
            # Usar RUT como ID del documento
            doc_ref = self.db.collection('usuarios').document(rut)
            doc_ref.set(usuario_data)
            
            usuario_data['id'] = rut
            return usuario_data
            
        except Exception as e:
            print(f"Error creando usuario: {e}")
            raise
    
    def crear_usuario_multiple(self, nombre, rut, carrera, jornada='D', 
                               vectores_faciales=None, vector_promedio=None, 
                               imagen_base64=None):
        """
        Crea usuario con múltiples vectores faciales.
        
        Args:
            nombre (str): Nombre completo
            rut (str): RUT único
            carrera (str): Carrera del alumno
            jornada (str): 'D' (Diurna) o 'V' (Vespertina)
            vectores_faciales (list): Lista de vectores faciales
            vector_promedio (list): Vector promedio de todos
            imagen_base64 (str): Imagen en base64 (opcional)
        
        Returns:
            dict: Usuario creado con ID
        """
        try:
            # Verificar si ya existe
            if self.obtener_usuario_por_rut(rut):
                raise ValueError(f"Ya existe un usuario con RUT {rut}")
            
            usuario_data = {
                'nombre': nombre,
                'rut': rut,
                'carrera': carrera,
                'jornada': jornada,
                'imagen': imagen_base64,
                'vectores_faciales': vectores_faciales or [],
                'vector_promedio': vector_promedio,
                'cantidad_muestras': len(vectores_faciales) if vectores_faciales else 0,
                'fecha_registro': datetime.now().isoformat(),
                'activo': True,
                'tipo_registro': 'multiple'  # Para diferenciar de registros simples
            }
            
            # Usar RUT como ID del documento
            doc_ref = self.db.collection('usuarios').document(rut)
            doc_ref.set(usuario_data)
            
            usuario_data['id'] = rut
            return usuario_data
            
        except Exception as e:
            print(f"Error creando usuario múltiple: {e}")
            raise
    
    def obtener_usuario_por_rut(self, rut):
        """
        Obtiene un usuario por su RUT.
        
        Args:
            rut (str): RUT del usuario
        
        Returns:
            dict: Datos del usuario o None si no existe
        """
        try:
            doc_ref = self.db.collection('usuarios').document(rut)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
    
    def listar_usuarios(self, jornada=None):
        """
        Lista todos los usuarios, opcionalmente filtrados por jornada.
        
        Args:
            jornada (str): 'D', 'N' o None para todos
        
        Returns:
            list: Lista de usuarios
        """
        try:
            query = self.db.collection('usuarios')
            
            if jornada:
                query = query.where('jornada', '==', jornada)
            
            query = query.order_by('nombre')
            
            usuarios = []
            for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                usuarios.append(data)
            
            return usuarios
            
        except Exception as e:
            print(f"Error listando usuarios: {e}")
            return []
    
    def actualizar_usuario(self, rut, **campos):
        """
        Actualiza campos de un usuario.
        
        Args:
            rut (str): RUT del usuario
            **campos: Campos a actualizar
        
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            doc_ref = self.db.collection('usuarios').document(rut)
            
            if not doc_ref.get().exists:
                raise ValueError(f"Usuario con RUT {rut} no existe")
            
            doc_ref.update(campos)
            return True
            
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False
    
    def actualizar_vector_facial(self, rut, vector_facial):
        """
        Actualiza el vector facial de un usuario.
        
        Args:
            rut (str): RUT del usuario
            vector_facial (list): Vector de 512 floats
        
        Returns:
            bool: True si se actualizó correctamente
        """
        return self.actualizar_usuario(
            rut,
            vector_facial=vector_facial,
            fecha_actualizacion_vector=datetime.now().isoformat()
        )
    
    def actualizar_foto_usuario(self, rut, imagen_base64):
        """
        Actualiza la foto de perfil de un usuario.
        
        Args:
            rut (str): RUT del usuario
            imagen_base64 (str): Imagen en base64 con data URI
        
        Returns:
            bool: True si se actualizó correctamente
        """
        return self.actualizar_usuario(
            rut,
            imagen=imagen_base64,
            fecha_actualizacion_foto=datetime.now().isoformat()
        )
    

    def eliminar_usuario(self, rut):
        """
        Elimina un usuario (soft delete - marca como inactivo).
        
        Args:
            rut (str): RUT del usuario
        
        Returns:
            bool: True si se eliminó correctamente
        """
        return self.actualizar_usuario(rut, activo=False)
    
    # ==========================================
    # GESTIÓN DE EVENTOS
    # ==========================================
    
    def crear_evento(self, nombre, descripcion, fecha, hora_inicio, hora_fin, relator, ubicacion):
        """
        Crea un nuevo evento en Firestore.
        """
        try:
            evento_data = {
                'nombre': nombre,
                'descripcion': descripcion,
                'fecha': fecha,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'relator': relator,
                'ubicacion': ubicacion,
                'estado': 'pendiente',  # pendiente, activo, finalizado
                'fecha_creacion': datetime.now().isoformat()
            }
            
            # Crear documento con ID automático
            doc_ref = self.db.collection('eventos').document()
            doc_ref.set(evento_data)
            
            evento_data['id'] = doc_ref.id
            return evento_data
            
        except Exception as e:
            print(f"Error creando evento: {e}")
            raise

    def listar_eventos(self):
        """
        Lista todos los eventos ordenados por fecha.
        """
        try:
            docs = self.db.collection('eventos').order_by('fecha', direction=firestore.Query.DESCENDING).stream()
            eventos = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                eventos.append(data)
            return eventos
        except Exception as e:
            print(f"Error listando eventos: {e}")
            return []

    def obtener_evento(self, evento_id):
        """Obtiene un evento por ID."""
        try:
            doc = self.db.collection('eventos').document(evento_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            print(f"Error obteniendo evento: {e}")
            return None

    def actualizar_evento(self, evento_id, **campos):
        """Actualiza un evento."""
        try:
            self.db.collection('eventos').document(evento_id).update(campos)
            return True
        except Exception as e:
            print(f"Error actualizando evento: {e}")
            return False

    def eliminar_evento(self, evento_id):
        """Elimina un evento."""
        try:
            self.db.collection('eventos').document(evento_id).delete()
            return True
        except Exception as e:
            print(f"Error eliminando evento: {e}")
            return False

    def verificar_superposicion_evento(self, fecha, hora_inicio, hora_fin, excluir_id=None):
        """
        Verifica si existe un evento activo/pendiente que se superponga con el horario dado.
        
        Args:
            fecha (str): Fecha del evento (YYYY-MM-DD)
            hora_inicio (str): Hora de inicio (HH:MM)
            hora_fin (str): Hora de fin (HH:MM)
            excluir_id (str): ID del evento a excluir (para edición)
        
        Returns:
            dict: Evento en conflicto o None si no hay superposición
        """
        try:
            from datetime import time
            
            # Parsear horas del nuevo evento
            h_inicio_nuevo = time.fromisoformat(hora_inicio)
            h_fin_nuevo = time.fromisoformat(hora_fin)
            
            # Buscar eventos en la misma fecha
            docs = self.db.collection('eventos').where('fecha', '==', fecha).stream()
            
            for doc in docs:
                # Excluir el evento actual si estamos editando
                if excluir_id and doc.id == excluir_id:
                    continue
                
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Solo considerar eventos activos o pendientes (no finalizados)
                estado = data.get('estado', 'pendiente')
                if estado == 'finalizado':
                    continue
                
                # Parsear horas del evento existente
                try:
                    h_inicio_existente = time.fromisoformat(data.get('hora_inicio', '00:00'))
                    h_fin_existente = time.fromisoformat(data.get('hora_fin', '23:59'))
                except:
                    continue
                
                # Verificar superposición de horarios
                # Hay superposición si: inicio_nuevo < fin_existente AND fin_nuevo > inicio_existente
                if h_inicio_nuevo < h_fin_existente and h_fin_nuevo > h_inicio_existente:
                    return data  # Retorna el evento en conflicto
            
            return None  # No hay superposición
            
        except Exception as e:
            print(f"Error verificando superposición: {e}")
            return None

    def obtener_evento_activo(self):
        """
        Busca un evento activo basado en fecha Y hora actual.
        Estados:
        - pendiente: fecha futura o fecha=hoy pero hora_actual < hora_inicio
        - activo: fecha=hoy y hora_inicio <= hora_actual <= hora_fin
        - finalizado: fecha pasada o fecha=hoy pero hora_actual > hora_fin
        
        Actualiza automáticamente el estado del evento si es necesario.
        """
        try:
            from datetime import time
            ahora = datetime.now()
            hoy = ahora.strftime("%Y-%m-%d")
            hora_actual = ahora.time()
            
            # Buscar eventos de hoy
            docs = self.db.collection('eventos').where('fecha', '==', hoy).stream()
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Parsear horas (formato HH:MM)
                try:
                    h_inicio = time.fromisoformat(data['hora_inicio'])
                    h_fin = time.fromisoformat(data['hora_fin'])
                except:
                    # Si no se pueden parsear las horas, saltar este evento
                    continue
                
                # Verificar si está en el rango de tiempo
                if h_inicio <= hora_actual <= h_fin:
                    # Actualizar estado a 'activo' si no lo está
                    if data.get('estado') != 'activo':
                        self.actualizar_evento(doc.id, estado='activo')
                        data['estado'] = 'activo'
                        print(f"✓ Evento '{data['nombre']}' activado automáticamente")
                    return data
                elif hora_actual > h_fin:
                    # Marcar como finalizado si ya pasó
                    if data.get('estado') != 'finalizado':
                        self.actualizar_evento(doc.id, estado='finalizado')
                        print(f"⏹ Evento '{data['nombre']}' finalizado automáticamente")
            
            return None
        except Exception as e:
            print(f"Error buscando evento activo: {e}")
            return None

    def actualizar_estados_eventos(self):
        """
        Actualiza el estado de TODOS los eventos según su fecha/hora.
        Útil para ejecutar periódicamente o al listar eventos.
        
        Lógica:
        - Eventos pasados (fecha < hoy) → 'finalizado'
        - Eventos de hoy fuera de horario → 'finalizado' o 'pendiente'
        - Eventos en horario actual → 'activo'
        - Eventos futuros → 'pendiente'
        """
        try:
            from datetime import time
            ahora = datetime.now()
            hoy = ahora.strftime("%Y-%m-%d")
            hora_actual = ahora.time()
            
            # Obtener todos los eventos
            docs = self.db.collection('eventos').stream()
            
            actualizados = 0
            for doc in docs:
                data = doc.to_dict()
                fecha_evento = data.get('fecha', '')
                estado_actual = data.get('estado', '')
                nuevo_estado = None
                
                # Comparar fechas
                if fecha_evento < hoy:
                    # Evento pasado
                    if estado_actual != 'finalizado':
                        nuevo_estado = 'finalizado'
                elif fecha_evento == hoy:
                    # Evento de hoy: verificar hora
                    try:
                        h_inicio = time.fromisoformat(data.get('hora_inicio', '00:00'))
                        h_fin = time.fromisoformat(data.get('hora_fin', '23:59'))
                        
                        if hora_actual < h_inicio:
                            if estado_actual != 'pendiente':
                                nuevo_estado = 'pendiente'
                        elif h_inicio <= hora_actual <= h_fin:
                            if estado_actual != 'activo':
                                nuevo_estado = 'activo'
                        else:  # hora_actual > h_fin
                            if estado_actual != 'finalizado':
                                nuevo_estado = 'finalizado'
                    except:
                        # Si no se pueden parsear las horas, dejar como está
                        pass
                else:
                    # Evento futuro
                    if estado_actual != 'pendiente':
                        nuevo_estado = 'pendiente'
                
                # Actualizar si cambió el estado
                if nuevo_estado:
                    self.actualizar_evento(doc.id, estado=nuevo_estado)
                    actualizados += 1
                    
            if actualizados > 0:
                print(f"🔄 {actualizados} evento(s) actualizados automáticamente")
                    
        except Exception as e:
            print(f"Error actualizando estados: {e}")

    # ==========================================
    # GESTIÓN DE ASISTENCIAS
    # ==========================================

    def registrar_asistencia(self, rut_usuario, id_evento, metodo='manual', similitud=None):
        """
        Registra la asistencia de un usuario a un evento.
        """
        try:
            # Verificar si ya existe asistencia
            docs = self.db.collection('asistencias')\
                .where('rut_usuario', '==', rut_usuario)\
                .where('id_evento', '==', id_evento)\
                .stream()
                
            for doc in docs:
                return {'status': 'existe', 'id': doc.id}

            asistencia_data = {
                'rut_usuario': rut_usuario,
                'id_evento': id_evento,
                'fecha_hora': datetime.now().isoformat(),
                'metodo': metodo,  # manual, biometrico
                'similitud': similitud,
                'verificado': True
            }
            
            doc_ref = self.db.collection('asistencias').document()
            doc_ref.set(asistencia_data)
            
            asistencia_data['id'] = doc_ref.id
            return {'status': 'registrada', 'data': asistencia_data}
            
        except Exception as e:
            print(f"Error registrando asistencia: {e}")
            raise

    def listar_asistencias(self, id_evento=None):
        """
        Lista asistencias, opcionalmente filtradas por evento.
        """
        try:
            ref = self.db.collection('asistencias')
            if id_evento:
                # Cuando filtramos por evento, NO ordenamos en Firebase
                # para evitar requerir índice compuesto
                ref = ref.where('id_evento', '==', id_evento)
                docs = ref.stream()
            else:
                # Sin filtro, podemos ordenar directamente
                docs = ref.order_by('fecha_hora', direction=firestore.Query.DESCENDING).stream()
            
            asistencias = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Enriquecer con datos de usuario
                usuario = self.obtener_usuario_por_rut(data['rut_usuario'])
                if usuario:
                    data['nombre_usuario'] = usuario.get('nombre', 'Desconocido')
                    data['carrera_usuario'] = usuario.get('carrera', '')
                    data['jornada_usuario'] = usuario.get('jornada', '')
                
                asistencias.append(data)
            
            # Si filtramos por evento, ordenamos en Python
            if id_evento:
                asistencias.sort(key=lambda x: x.get('fecha_hora', ''), reverse=True)
            
            return asistencias
        except Exception as e:
            print(f"Error listando asistencias: {e}")
            return []


# Instancia global del servicio
firebase_service = FirebaseService()
