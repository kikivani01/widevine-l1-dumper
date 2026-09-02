# Widevine L1 Dumper

A tool to extract and dump Widevine L1 DRM credentials (client_id.bin and private_key.pem) from Android devices with Widevine L1 certification.

## Overview

This tool facilitates the extraction of Widevine L1 client identification and private key files from Android devices. These files are essential for testing and analysis of Widevine DRM implementations on protected devices.

**Disclaimer:** This tool is intended for educational and authorized testing purposes only. Unauthorized extraction of DRM credentials may violate the DMCA and other applicable laws.

## Requirements

- Android device with Widevine L1 certification
- Android Debug Bridge (ADB) enabled on the device
- Python 3.8+
- USB debugging enabled on the device

## Installation

```bash
git clone https://github.com/kikivani01/widevine-l1-dumper.git
cd widevine-l1-dumper
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python widevine_dumper.py --device <device_serial>
```

### Extract Files to Custom Location

```bash
python widevine_dumper.py --device <device_serial> --output ./credentials
```

### Verbose Output

```bash
python widevine_dumper.py --device <device_serial> -v
```

## Output

The tool will extract and save:

- `client_id.bin` - Widevine client identification blob
- `private_key.pem` - Widevine private key in PEM format

Files are saved in the output directory (default: `./widevine_keys/`)

## Project Structure

```
widevine-l1-dumper/
├── README.md
├── requirements.txt
├── widevine_dumper.py          # Main entry point
├── src/
│   ├── adb_handler.py          # ADB device communication
│   ├── key_extractor.py        # Key extraction logic
│   ├── key_parser.py           # Parse extracted key data
│   └── utils.py                # Utility functions
├── lib/
│   └── widevine/               # Widevine-related modules
│       ├── client.py           # Widevine client interaction
│       └── constants.py        # Constants and configuration
├── scripts/
│   └── setup_device.sh         # Device setup helper
└── examples/
    └── extract_example.py      # Usage examples
```

## Supported Devices

This tool works with Android devices that meet the following criteria:

- Widevine L1 certification
- Android 5.0 (API level 21) or higher
- USB debugging enabled

## Security Considerations

- Keep extracted keys secure and confidential
- Use this tool only on devices you own or have authorization to test
- Consider encrypting extracted key files
- Do not share keys or credentials publicly

## Troubleshooting

### Device Not Found

Ensure ADB is properly installed and USB debugging is enabled:

```bash
adb devices
```

### Permission Denied

Some devices require rooting or elevated privileges to access key storage locations. Ensure your device is properly authorized.

### ADB Connection Issues

- Restart the ADB server: `adb kill-server && adb start-server`
- Check USB cable connection
- Verify USB debugging is enabled in Developer Options

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome. Please ensure any modifications maintain the security and integrity of the key extraction process.

## References

- [Widevine DRM](https://www.widevine.com/)
- [Android Debug Bridge (ADB)](https://developer.android.com/studio/command-line/adb)
- [Widevine L1 Certification](https://www.widevine.com/solutions/certified-devices)

---

**Warning:** Use this tool responsibly and only on devices you own or have explicit authorization to test.
