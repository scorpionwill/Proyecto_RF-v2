import cv2
import sys
import os

# Add project root to path to import service
sys.path.append('/root/Proyecto_RF/prototipo_2.0')

from reconocimiento_facial.usuarios.services.inspireface_service import inspireface_service

IMAGE_PATH = '/root/Proyecto_RF/prototipo_2.0/reconocimiento_facial/usuarios/static/images/usuario_placeholder.png'

def test_service():
    print(f"Testing InspireFaceService with image: {IMAGE_PATH}")
    
    # Load image
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print("❌ Failed to load image")
        return
    
    print(f"Image loaded: {image.shape}")
    
    # Get embedding
    print("Generating embedding...")
    embedding = inspireface_service.get_face_embedding(image)
    
    if embedding:
        print("✅ Embedding generated successfully")
        print(f"Embedding type: {type(embedding)}")
        print(f"Embedding length: {len(embedding)}")
        
        if isinstance(embedding, list) and len(embedding) == 512:
            print("✅ Verification PASSED: Embedding is a list of 512 floats")
        else:
            print("❌ Verification FAILED: Invalid embedding format")
    else:
        print("❌ Verification FAILED: No embedding generated (Face not detected?)")

if __name__ == "__main__":
    test_service()
