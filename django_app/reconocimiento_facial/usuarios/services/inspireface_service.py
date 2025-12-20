"""
-----------------------------------------------------------------------------
Archivo: inspireface_service.py
Descripcion: Servicio singleton para el SDK InspireFace. Proporciona
             deteccion de rostros, extraccion de vectores faciales de
             512 dimensiones, y evaluacion de calidad de imagen.
             Actua como interfaz entre Django y el motor de IA biometrico.
Fecha de creacion: 05 de Octubre 2025
Fecha de modificacion: 20 de Diciembre 2025
Autores:
    Roberto Leal
    William Tapia
-----------------------------------------------------------------------------
"""
import inspireface as isf
import cv2
import numpy as np


class InspireFaceService:
    """
    Servicio singleton para el SDK de InspireFace.
    Proporciona detección de rostros, extracción de características y evaluación de calidad.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InspireFaceService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialize_sdk()
            self._initialized = True

    def _initialize_sdk(self):
        """Inicializa el SDK de InspireFace y la sesión con configuración óptima"""
        print("🚀 Inicializando SDK InspireFace...")
        
        # Inicializar SDK globalmente
        ret = isf.reload()
        if not ret:
            raise RuntimeError("Error al inicializar SDK InspireFace")
        
        # Crear sesión con flags optimizados
        # Habilitar solo lo necesario: reconocimiento facial y evaluación de calidad
        opt = isf.HF_ENABLE_FACE_RECOGNITION
        
        # Usar modo de detección continua para precisión en registro/reconocimiento
        self.session = isf.InspireFaceSession(
            opt, 
            isf.HF_DETECT_MODE_ALWAYS_DETECT,
            max_detect_num=5  # Soportar hasta 5 rostros para escenarios grupales
        )
        
        # Establecer umbral óptimo de confianza de detección
        self.session.set_detection_confidence_threshold(0.4)
        
        # Establecer tamaño mínimo de rostro en píxeles para filtrar rostros muy pequeños
        self.session.set_filter_minimum_face_pixel_size(80)
        
        print("✅ Sesión InspireFace Creada")

    def get_face_embedding(self, image, return_quality=False):
        """
        Detecta rostro y retorna embedding con puntaje de calidad opcional.
        
        Args:
            image: Imagen de entrada (numpy array)
            return_quality: Si es True, retorna tupla (embedding, puntaje_calidad)
            
        Returns:
            embedding (list): Vector de 512 dimensiones o None si no hay rostro/error
            Si return_quality=True: (embedding, puntaje_calidad) o (None, 0)
        """
        try:
            if image is None:
                return (None, 0.0) if return_quality else None

            # Realizar detección
            faces = self.session.face_detection(image)
            
            if not faces:
                print("  ⚠️ InspireFace: 0 rostros detectados")
                return (None, 0.0) if return_quality else None
            
            print(f"  ✅ InspireFace: {len(faces)} rostros detectados")
            
            # Obtener el mejor rostro (más grande/centrado)
            best_face = self._select_best_face(faces)
            
            # Extraer característica
            feature = self.session.face_feature_extract(image, best_face)
            
            # Convertir a lista
            embedding = list(feature.data) if hasattr(feature, 'data') else list(feature)
            
            if return_quality:
                # Calcular puntaje de calidad basado en tamaño y confianza de detección
                quality = self._calculate_face_quality(best_face, image.shape)
                return (embedding, quality)
            
            return embedding
            
        except Exception as e:
            print(f"❌ Error InspireFace: {e}")
            return (None, 0.0) if return_quality else None

    def get_multiple_embeddings(self, image):
        """
        Detecta múltiples rostros y retorna todos los embeddings.
        Útil para procesamiento por lotes o escenarios grupales.
        
        Returns:
            Lista de tuplas (embedding, ubicación_rostro)
        """
        try:
            if image is None:
                return []

            faces = self.session.face_detection(image)
            
            if not faces:
                return []
            
            results = []
            for face in faces:
                try:
                    feature = self.session.face_feature_extract(image, face)
                    embedding = list(feature.data) if hasattr(feature, 'data') else list(feature)
                    results.append((embedding, face.location))
                except Exception as e:
                    print(f"⚠️ Error al extraer característica de un rostro: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ Error InspireFace: {e}")
            return []

    def detect_faces(self, image):
        """
        Detecta todos los rostros en la imagen.
        Retorna lista de objetos de rostro con ubicaciones.
        """
        if image is None:
            return []
        try:
            return self.session.face_detection(image)
        except Exception:
            return []

    def _select_best_face(self, faces):
        """
        Selecciona el mejor rostro de múltiples detecciones.
        Prioriza: posición centrada > tamaño
        """
        if len(faces) == 1:
            return faces[0]
        
        # Para múltiples rostros, preferir el más centrado y grande
        def score_face(face):
            x1, y1, x2, y2 = face.location
            # Puntaje por tamaño
            area = (x2 - x1) * (y2 - y1)
            # Puntaje por centrado (distancia al centro, normalizada)
            # Asumiendo que no tenemos dimensiones de imagen, usar área relativa como proxy
            return area
        
        return max(faces, key=score_face)

    def _calculate_face_quality(self, face, image_shape):
        """
        Calcula puntaje de calidad del rostro basado en tamaño y posición.
        Retorna valor entre 0-1.
        """
        x1, y1, x2, y2 = face.location
        face_width = x2 - x1
        face_height = y2 - y1
        img_height, img_width = image_shape[:2]
        
        # Ratio de tamaño (rostros más grandes = mejor calidad)
        size_ratio = (face_width * face_height) / (img_width * img_height)
        
        # Normalizar a rango 0-1 (asumir que 0.05-0.5 es buen rango)
        quality = min(1.0, max(0.0, (size_ratio - 0.02) / 0.3))
        
        return quality

    def compare_features(self, feature1, feature2):
        """
        Compara dos características faciales usando comparación nativa de InspireFace.
        
        Args:
            feature1: Primer embedding (lista de 512 floats)
            feature2: Segundo embedding (lista de 512 floats)
            
        Returns:
            puntaje de similitud (0-1)
        """
        # Convertir a numpy para similitud coseno
        vec1 = np.array(feature1)
        vec2 = np.array(feature2)
        
        # Similitud coseno
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Limitar a rango [0, 1]
        return max(0.0, min(1.0, similarity))


# Instancia singleton global
inspireface_service = InspireFaceService()
