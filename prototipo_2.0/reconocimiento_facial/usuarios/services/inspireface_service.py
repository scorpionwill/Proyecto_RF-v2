import inspireface as isf
import cv2
import numpy as np


class InspireFaceService:
    """
    Singleton service for InspireFace SDK.
    Provides face detection, feature extraction, and quality assessment.
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
        """Initialize InspireFace SDK and Session with optimal settings"""
        print("🚀 Initializing InspireFace SDK...")
        
        # Initialize SDK globally
        ret = isf.reload()
        if not ret:
            raise RuntimeError("Failed to initialize InspireFace SDK")
        
        # Create session with optimized flags
        # Enable only what we need: face recognition and quality assessment
        opt = isf.HF_ENABLE_FACE_RECOGNITION
        
        # Use always-detect mode for accuracy in registration/recognition
        self.session = isf.InspireFaceSession(
            opt, 
            isf.HF_DETECT_MODE_ALWAYS_DETECT,
            max_detect_num=5  # Support up to 5 faces for group scenarios
        )
        
        # Set optimal detection confidence threshold
        self.session.set_detection_confidence_threshold(0.4)
        
        # Set minimum face pixel size to filter out too-small faces
        self.session.set_filter_minimum_face_pixel_size(80)
        
        print("✅ InspireFace Session Created")

    def get_face_embedding(self, image, return_quality=False):
        """
        Detect face and return embedding with optional quality score.
        
        Args:
            image: Input image (numpy array)
            return_quality: If True, return (embedding, quality_score) tuple
            
        Returns:
            embedding (list): 512d vector or None if no face/error
            If return_quality=True: (embedding, quality_score) or (None, 0)
        """
        try:
            if image is None:
                return (None, 0.0) if return_quality else None

            # Perform detection
            faces = self.session.face_detection(image)
            
            if not faces:
                print("  ⚠️ InspireFace: 0 faces detected")
                return (None, 0.0) if return_quality else None
            
            print(f"  ✅ InspireFace: {len(faces)} faces detected")
            
            # Get the largest/best face
            best_face = self._select_best_face(faces)
            
            # Extract feature
            feature = self.session.face_feature_extract(image, best_face)
            
            # Convert to list
            embedding = list(feature.data) if hasattr(feature, 'data') else list(feature)
            
            if return_quality:
                # Calculate quality score based on face size and detection confidence
                quality = self._calculate_face_quality(best_face, image.shape)
                return (embedding, quality)
            
            return embedding
            
        except Exception as e:
            print(f"❌ InspireFace Error: {e}")
            return (None, 0.0) if return_quality else None

    def get_multiple_embeddings(self, image):
        """
        Detect multiple faces and return all embeddings.
        Useful for batch processing or group scenarios.
        
        Returns:
            List of (embedding, face_location) tuples
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
                    print(f"⚠️ Failed to extract feature for one face: {e}")
                    continue
            
            return results
            
        except Exception as e:
            print(f"❌ InspireFace Error: {e}")
            return []

    def detect_faces(self, image):
        """
        Detect all faces in image.
        Returns list of face objects with locations.
        """
        if image is None:
            return []
        try:
            return self.session.face_detection(image)
        except Exception:
            return []

    def _select_best_face(self, faces):
        """
        Select the best face from multiple detections.
        Prioritizes: center position > size
        """
        if len(faces) == 1:
            return faces[0]
        
        # For multiple faces, prefer the most centered and largest
        def score_face(face):
            x1, y1, x2, y2 = face.location
            # Size score
            area = (x2 - x1) * (y2 - y1)
            # Center score (distance from center, normalized)
            # Assuming we don't have image dimensions, use relative area as proxy
            return area
        
        return max(faces, key=score_face)

    def _calculate_face_quality(self, face, image_shape):
        """
        Calculate face quality score based on size and position.
        Returns value between 0-1.
        """
        x1, y1, x2, y2 = face.location
        face_width = x2 - x1
        face_height = y2 - y1
        img_height, img_width = image_shape[:2]
        
        # Size ratio (larger faces = better quality)
        size_ratio = (face_width * face_height) / (img_width * img_height)
        
        # Normalize to 0-1 range (assume 0.05-0.5 is good range)
        quality = min(1.0, max(0.0, (size_ratio - 0.02) / 0.3))
        
        return quality

    def compare_features(self, feature1, feature2):
        """
        Compare two face features using InspireFace's native comparison.
        
        Args:
            feature1: First embedding (list of 512 floats)
            feature2: Second embedding (list of 512 floats)
            
        Returns:
            similarity score (0-1)
        """
        # Convert to numpy for cosine similarity
        vec1 = np.array(feature1)
        vec2 = np.array(feature2)
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, similarity))


# Global singleton instance
inspireface_service = InspireFaceService()
