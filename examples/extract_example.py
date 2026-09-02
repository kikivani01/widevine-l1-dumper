#!/usr/bin/env python3
"""Example: Extract Widevine L1 keys from connected device."""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adb_handler import ADBHandler
from src.key_extractor import KeyExtractor
from src.utils import setup_logging, ensure_output_dir


def main():
    """Main extraction example."""
    # Setup logging
    setup_logging(verbose=True)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("Widevine L1 Key Extractor - Example")
    logger.info("=" * 60)
    
    # Create ADB handler
    adb = ADBHandler()
    
    # Select device
    logger.info("\nStep 1: Selecting device...")
    if not adb.select_device():
        logger.error("Failed to select device")
        return 1
    
    # Get device info
    logger.info("\nStep 2: Getting device information...")
    device_info = adb.get_device_info()
    for key, value in device_info.items():
        logger.info(f"  {key}: {value}")
    
    # Create key extractor
    logger.info("\nStep 3: Initializing key extractor...")
    extractor = KeyExtractor(adb)
    
    # Extract keys
    output_dir = ensure_output_dir("./widevine_keys")
    logger.info(f"\nStep 4: Extracting keys to {output_dir}...")
    
    success, client_id_path, private_key_path = extractor.extract_keys(output_dir)
    
    # Verify extracted keys
    logger.info("\nStep 5: Verifying extracted keys...")
    if extractor.verify_extracted_keys(client_id_path, private_key_path):
        logger.info("✓ All keys verified successfully!")
    else:
        logger.warning("⚠ Some keys failed verification")
    
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("✓ Key extraction completed successfully!")
        if client_id_path:
            logger.info(f"  client_id.bin: {client_id_path}")
        if private_key_path:
            logger.info(f"  private_key.pem: {private_key_path}")
        return 0
    else:
        logger.error("✗ Key extraction failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
