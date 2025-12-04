import inspireface as isf

print("Inspecting InspireFace SDK...")
try:
    ret = isf.reload()
    session = isf.InspireFaceSession(isf.HF_ENABLE_FACE_RECOGNITION, isf.HF_DETECT_MODE_ALWAYS_DETECT)
    
    print("\nSession methods:")
    for method in dir(session):
        if not method.startswith("__"):
            print(method)
            
    print("\nModule attributes:")
    for attr in dir(isf):
        if not attr.startswith("__"):
            print(attr)

except Exception as e:
    print(f"Error: {e}")
