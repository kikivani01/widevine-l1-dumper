# Widevine L1 Dumper - Quick Start

## Installation

### Prerequisites
- Python 3.8 or higher
- ADB (Android Debug Bridge)
- Android device with Widevine L1 certification
- USB debugging enabled on device

### Step 1: Clone Repository

```bash
git clone https://github.com/kikivani01/widevine-l1-dumper.git
cd widevine-l1-dumper
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify ADB Installation

```bash
adb version
adb devices
```

## Usage

### List Connected Devices

```bash
python widevine_dumper.py --list-devices
```

### Show Device Information

```bash
python widevine_dumper.py --show-device-info
```

### Extract Keys

```bash
# From auto-selected device
python widevine_dumper.py

# From specific device
python widevine_dumper.py --device <device_serial>

# To custom output directory
python widevine_dumper.py --output ./my_keys

# With verbose logging
python widevine_dumper.py -v

# With log file
python widevine_dumper.py --log-file extraction.log
```

### Verify Existing Keys

```bash
python widevine_dumper.py --verify-only --output ./widevine_keys
```

## Output Files

The tool extracts two key files:

- **client_id.bin** - Widevine client identification blob (binary format)
- **private_key.pem** - Widevine private key (PEM format)

Both files are saved to the output directory (default: `./widevine_keys/`)

## Security

⚠️ **IMPORTANT SECURITY WARNING** ⚠️

- These extracted keys are CONFIDENTIAL DRM credentials
- Keep them secure and never share publicly
- Use only for authorized testing on your own devices
- Unauthorized extraction may violate the DMCA
- Store keys with proper file permissions (chmod 600)
- Consider encrypting extracted keys at rest

## Troubleshooting

### "ADB not found"
Install Android SDK Platform Tools:
- Linux: `sudo apt-get install android-tools-adb`
- macOS: `brew install android-platform-tools`
- Windows: Download from [Android SDK](https://developer.android.com/studio)

### "No devices found"
- Enable USB debugging on device
- Check USB connection
- Run: `adb kill-server && adb start-server`

### "Permission denied"
- Device may require root access
- Check device storage permissions
- Some keys may be in restricted locations

### "Keys not found"
- Device may not store keys in default locations
- Try with verbose logging: `python widevine_dumper.py -v`
- Check device's Widevine implementation

## Advanced Usage

### Run with Example Script

```bash
python examples/extract_example.py
```

### Custom Python Usage

```python
from src.adb_handler import ADBHandler
from src.key_extractor import KeyExtractor

# Initialize ADB
adb = ADBHandler(device_serial="emulator-5554")
adb.select_device()

# Extract keys
extractor = KeyExtractor(adb)
success, client_id_path, private_key_path = extractor.extract_keys("./my_keys")
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the [GitHub Issues](https://github.com/kikivani01/widevine-l1-dumper/issues)
2. Enable verbose logging: `python widevine_dumper.py -v`
3. Check log files for detailed error information

## References

- [Widevine DRM](https://www.widevine.com/)
- [Android Debug Bridge](https://developer.android.com/studio/command-line/adb)
- [Android Security](https://source.android.com/security)
