import inspireface as isf
import os

print("Testing InspireFace...")
try:
    ret = isf.reload()
    print(f"Reload returned: {ret}")
    if ret:
        print("✅ InspireFace initialized successfully")
    else:
        print("❌ InspireFace initialization failed")
except Exception as e:
    print(f"❌ Error: {e}")
