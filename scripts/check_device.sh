#!/bin/bash
# Device setup helper - checks device readiness for key extraction

echo "Widevine L1 Dumper - Device Setup Helper"
echo "========================================"

# Check if device serial is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <device_serial>"
    echo "Example: $0 emulator-5554"
    exit 1
fi

DEVICE=$1

echo "\nChecking device: $DEVICE"

# Check if device is connected
echo "\n[1/5] Checking device connection..."
if adb -s $DEVICE shell echo OK > /dev/null 2>&1; then
    echo "✓ Device is connected and responsive"
else
    echo "✗ Device is not accessible"
    exit 1
fi

# Get device info
echo "\n[2/5] Getting device information..."
echo "  Model: $(adb -s $DEVICE shell getprop ro.product.model)"
echo "  Brand: $(adb -s $DEVICE shell getprop ro.product.brand)"
echo "  Android: $(adb -s $DEVICE shell getprop ro.build.version.release)"
echo "  API Level: $(adb -s $DEVICE shell getprop ro.build.version.sdk)"

# Check for root
echo "\n[3/5] Checking for root access..."
if adb -s $DEVICE shell su -c "id" > /dev/null 2>&1; then
    echo "✓ Root access available (superuser)"
else
    echo "⚠ Root access not available (may limit key extraction)"
fi

# Check for common Widevine paths
echo "\n[4/5] Checking for Widevine paths..."
PATHS=(
    "/data/misc/widevine/"
    "/data/media/widevine/"
    "/data/mediadrm/"
    "/cache/widevine/"
    "/persist/widevine/"
)

for path in "${PATHS[@]}"; do
    if adb -s $DEVICE shell test -d "$path" > /dev/null 2>&1; then
        echo "✓ Found: $path"
    fi
done

# Check storage space
echo "\n[5/5] Checking storage space..."
STORAGE=$(adb -s $DEVICE shell df /data | tail -1 | awk '{print $4}')
echo "  Available space: ${STORAGE}K ($(echo "scale=2; $STORAGE/1024" | bc)M)"

if [ "$STORAGE" -gt 10000 ]; then
    echo "✓ Sufficient storage space"
else
    echo "⚠ Low storage space"
fi

echo "\n========================================"
echo "✓ Device check completed"
echo "========================================"
echo "\nDevice is ready for key extraction."
echo "Run: python widevine_dumper.py --device $DEVICE"
