"""Widevine constants and configuration."""

# Widevine DRM system ID
WIDEVINE_SYSTEM_ID = "edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"

# Security levels
SECURITY_LEVEL_L1 = "L1"
SECURITY_LEVEL_L2 = "L2"
SECURITY_LEVEL_L3 = "L3"

# Widevine certification levels
CERTIFICATION_LEVELS = {
    1: "L1 - Hardware-backed DRM (TEE)",
    2: "L2 - Host-backed DRM",
    3: "L3 - Software-based DRM",
}

# Common Widevine paths on Android
WIDEVINE_COMMON_PATHS = [
    "/data/misc/widevine/",
    "/data/media/widevine/",
    "/data/mediadrm/",
    "/cache/widevine/",
    "/persist/widevine/",
    "/data/vendor/widevine/",
]

# Key file patterns
CLIENT_ID_PATTERNS = ["client_id.bin", "clientid.bin", "widevine_client_id.bin"]
PRIVATE_KEY_PATTERNS = ["private_key.pem", "privatekey.pem", "widevine_key.pem"]
