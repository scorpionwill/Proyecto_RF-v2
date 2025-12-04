"""
Configuration constants for the face recognition system.
Centralized location for all configuration values.
"""

# ==========================================
# RTSP Camera Configuration
# ==========================================
LUCKFOX_IP = '172.32.0.93'
LUCKFOX_PORT = 8080
RTSP_URL_HIGH = f'rtsp://{LUCKFOX_IP}/live/0'  # 2592x1944 (máxima calidad)
RTSP_URL_LOW = f'rtsp://{LUCKFOX_IP}/live/1'   # Baja resolución

# ==========================================
# Video Processing Configuration
# ==========================================
VIDEO_RESOLUTION = (1920, 1080)  # Full HD
VIDEO_BUFFER_SIZE = 1
VIDEO_FPS = 30
JPEG_QUALITY = 95

# ==========================================
# Face Recognition Thresholds
# ==========================================
# InspireFace similarity thresholds (cosine similarity: 0-1)
SIMILARITY_THRESHOLD_DEFAULT = 0.48  # Default matching threshold
SIMILARITY_THRESHOLD_STRICT = 0.60   # Strict threshold for immediate confirmation
SIMILARITY_THRESHOLD_VERIFICATION = 0.70  # 1:1 verification

# Detection thresholds
DETECTION_CONFIDENCE_THRESHOLD = 0.5
MIN_FACE_PIXEL_SIZE = 80
MAX_FACES_TO_DETECT = 5

# Quality thresholds
MIN_FACE_QUALITY = 0.3  # Minimum quality score to accept face

# ==========================================
# Capture Configuration
# ==========================================
CAPTURE_FRAMES_COUNT = 10  # Number of frames to capture for registration
CAPTURE_BUFFER_CLEANUP_FRAMES = 2  # Frames to discard for stabilization
CAPTURE_MIN_VALID_FRAMES = 5  # Minimum valid captures required
CAPTURE_MAX_ATTEMPTS = 60  # Maximum attempts to capture frames

# Profile photo capture
PROFILE_PHOTO_BUFFER_CLEANUP_FRAMES = 5

# ==========================================
# Recognition Configuration
# ==========================================
RECOGNITION_MAX_ATTEMPTS = 5  # Maximum recognition attempts
RECOGNITION_PERSISTENCE_THRESHOLD = 2  # Matching confirmations needed

# ==========================================
# Timeout Configuration
# ==========================================
SOCKET_TIMEOUT = 10  # Socket timeout in seconds
RTSP_CONNECTION_TIMEOUT = 30  # RTSP connection timeout

# ==========================================
# Database Configuration
# ==========================================
# Firebase collection names
COLLECTION_USERS = 'usuarios'
COLLECTION_EVENTS = 'eventos'
COLLECTION_ATTENDANCE = 'asistencias'

# ==========================================
# Outlier Filtering Configuration
# ==========================================
MAD_THRESHOLD_MULTIPLIER = 3  # Multiplier for MAD-based outlier detection
STDDEV_THRESHOLD_MULTIPLIER = 2  # Multiplier for std dev outlier detection

# ==========================================
# Logging Configuration
# ==========================================
LOG_EMOJI_ENABLED = True  # Use emojis in console logs
LOG_VERBOSE_MATCHING = True  # Verbose output during matching
