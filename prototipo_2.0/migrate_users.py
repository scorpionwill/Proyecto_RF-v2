import os
import sys
import cv2
import numpy as np
import base64
import django
from django.conf import settings

# Setup Django environment
sys.path.append('/root/Proyecto_RF/prototipo_2.0')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconocimiento_facial.settings')
django.setup()

from reconocimiento_facial.usuarios.services.firebase_service import firebase_service
from reconocimiento_facial.usuarios.services.inspireface_service import inspireface_service

def migrate_users():
    print("🚀 Starting migration to InspireFace...")
    
    users = firebase_service.listar_usuarios()
    print(f"📊 Found {len(users)} users in Firebase")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for user in users:
        rut = user.get('rut')
        nombre = user.get('nombre')
        imagen_b64 = user.get('imagen')
        
        print(f"\nProcessing {nombre} ({rut})...")
        
        if not imagen_b64:
            print("  ⚠️ No profile image found. Skipping.")
            skip_count += 1
            continue
            
        try:
            # Clean base64 string if needed
            if ',' in imagen_b64:
                imagen_b64 = imagen_b64.split(',')[1]
                
            # Decode image
            img_bytes = base64.b64decode(imagen_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print("  ❌ Failed to decode image.")
                fail_count += 1
                continue
                
            # Generate new embedding
            embedding = inspireface_service.get_face_embedding(img)
            
            if embedding:
                # Update Firebase
                firebase_service.actualizar_vector_facial(rut, embedding)
                print("  ✅ Vector updated successfully (InspireFace 512d)")
                success_count += 1
            else:
                print("  ❌ No face detected by InspireFace in profile photo.")
                fail_count += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            fail_count += 1
            
    print(f"\nMigration Complete!")
    print(f"✅ Updated: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"⏭️ Skipped: {skip_count}")

if __name__ == "__main__":
    migrate_users()
