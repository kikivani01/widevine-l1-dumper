#!/usr/bin/env python3
"""Widevine L1 Dumper - Main entry point.

This script extracts Widevine L1 DRM credentials (client_id.bin and private_key.pem)
from Android devices.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.adb_handler import ADBHandler
from src.key_extractor import KeyExtractor
from src.key_parser import KeyParser
from src.utils import setup_logging, ensure_output_dir


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser.
    
    Returns:
        ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="Widevine L1 Dumper - Extract client_id.bin and private_key.pem from Android devices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract keys from first available device
  python widevine_dumper.py
  
  # Extract keys from specific device
  python widevine_dumper.py --device emulator-5554
  
  # Extract to custom location
  python widevine_dumper.py --output ./my_credentials
  
  # Verbose output
  python widevine_dumper.py -v
  
  # List available devices
  python widevine_dumper.py --list-devices
        """
    )
    
    parser.add_argument(
        "--device", "-d",
        help="Device serial number",
        default=None
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output directory for extracted keys (default: ./widevine_keys)",
        default="./widevine_keys"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        help="Enable verbose logging",
        action="store_true"
    )
    
    parser.add_argument(
        "--list-devices", "-l",
        help="List connected devices and exit",
        action="store_true"
    )
    
    parser.add_argument(
        "--verify-only",
        help="Verify extracted keys without re-extracting",
        action="store_true"
    )
    
    parser.add_argument(
        "--show-device-info",
        help="Show device information and exit",
        action="store_true"
    )
    
    parser.add_argument(
        "--log-file",
        help="Save log output to file",
        default=None
    )
    
    return parser


def list_devices(adb: ADBHandler) -> int:
    """List connected devices.
    
    Args:
        adb: ADB handler instance.
        
    Returns:
        Exit code.
    """
    devices = adb.get_devices()
    
    if not devices:
        print("No devices found.")
        return 1
    
    print("Connected devices:")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    return 0


def show_device_info(adb: ADBHandler) -> int:
    """Show device information.
    
    Args:
        adb: ADB handler instance.
        
    Returns:
        Exit code.
    """
    logger = logging.getLogger(__name__)
    
    if not adb.select_device():
        return 1
    
    logger.info(f"Device: {adb.device_serial}")
    logger.info("\nDevice Information:")
    
    device_info = adb.get_device_info()
    for key, value in device_info.items():
        logger.info(f"  {key}: {value}")
    
    return 0


def verify_keys(output_dir: str) -> int:
    """Verify extracted keys.
    
    Args:
        output_dir: Directory containing extracted keys.
        
    Returns:
        Exit code.
    """
    logger = logging.getLogger(__name__)
    parser = KeyParser()
    
    client_id_path = os.path.join(output_dir, "client_id.bin")
    private_key_path = os.path.join(output_dir, "private_key.pem")
    
    logger.info("\nVerifying extracted keys...")
    logger.info(f"Output directory: {output_dir}")
    
    valid = True
    
    # Check client_id.bin
    if os.path.exists(client_id_path):
        info = parser.parse_client_id(client_id_path)
        if info:
            logger.info(f"\n✓ client_id.bin found")
            logger.info(f"  Size: {info['size']} bytes")
            logger.info(f"  Preview: {info['hex_preview'][:32]}...")
        else:
            logger.error("✗ client_id.bin verification failed")
            valid = False
    else:
        logger.warning(f"⚠ client_id.bin not found in {output_dir}")
    
    # Check private_key.pem
    if os.path.exists(private_key_path):
        info = parser.parse_private_key(private_key_path)
        if info:
            logger.info(f"\n✓ private_key.pem found")
            logger.info(f"  Size: {info['size']} bytes")
            logger.info(f"  Key Type: {info['key_type']}")
            logger.info(f"  Lines: {info['line_count']}")
        else:
            logger.error("✗ private_key.pem verification failed")
            valid = False
    else:
        logger.warning(f"⚠ private_key.pem not found in {output_dir}")
    
    return 0 if valid else 1


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code.
    """
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose, log_file=args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("Widevine L1 Dumper v1.0.0")
    logger.info("=" * 70)
    
    try:
        # Create ADB handler
        adb = ADBHandler(device_serial=args.device)
        
        # Handle list devices
        if args.list_devices:
            return list_devices(adb)
        
        # Handle show device info
        if args.show_device_info:
            return show_device_info(adb)
        
        # Handle verify only
        if args.verify_only:
            output_dir = ensure_output_dir(args.output)
            return verify_keys(output_dir)
        
        # Select device
        logger.info("\n[1/4] Selecting device...")
        if not adb.select_device():
            return 1
        
        logger.info(f"✓ Device selected: {adb.device_serial}")
        
        # Get device info
        logger.info("\n[2/4] Getting device information...")
        device_info = adb.get_device_info()
        for key, value in device_info.items():
            logger.debug(f"  {key}: {value}")
        logger.info("✓ Device information retrieved")
        
        # Create key extractor
        logger.info("\n[3/4] Extracting Widevine keys...")
        output_dir = ensure_output_dir(args.output)
        logger.info(f"Output directory: {output_dir}")
        
        extractor = KeyExtractor(adb)
        success, client_id_path, private_key_path = extractor.extract_keys(output_dir)
        
        if not success:
            logger.error("✗ Key extraction failed")
            return 1
        
        logger.info("✓ Keys extracted successfully")
        
        # Verify extracted keys
        logger.info("\n[4/4] Verifying extracted keys...")
        if extractor.verify_extracted_keys(client_id_path, private_key_path):
            logger.info("✓ All keys verified")
        else:
            logger.warning("⚠ Some keys failed verification")
        
        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("✓ KEY EXTRACTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
        if client_id_path:
            logger.info(f"\nclient_id.bin:   {client_id_path}")
            logger.info(f"Size: {os.path.getsize(client_id_path)} bytes")
        
        if private_key_path:
            logger.info(f"\nprivate_key.pem: {private_key_path}")
            logger.info(f"Size: {os.path.getsize(private_key_path)} bytes")
        
        logger.info("\n" + "=" * 70)
        logger.warning("\nSECURITY WARNING:")
        logger.warning("  - Keep these keys secure and confidential")
        logger.warning("  - Do not share or publish these credentials")
        logger.warning("  - Use only for authorized testing")
        logger.warning("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"\nFatal error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
