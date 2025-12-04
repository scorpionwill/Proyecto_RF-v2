#!/bin/sh
# Stop existing camera apps
RkLunch-stop.sh
killall rkipc
killall luckfox_face_access  # Kill any previous instance

# Ensure library is in system path
if [ -f "/root/proyect_tesis/lib/libInspireFace.so" ]; then
    echo "Copying library to /usr/lib..."
    cp /root/proyect_tesis/lib/libInspireFace.so /usr/lib/
fi

# Run application
cd /root/proyect_tesis
./luckfox_face_access
