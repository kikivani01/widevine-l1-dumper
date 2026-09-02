"""Widevine L1 key extraction logic."""

import logging
import os
from pathlib import Path
from typing import Tuple, Optional
from src.adb_handler import ADBHandler
from src.key_parser import KeyParser

logger = logging.getLogger(__name__)


class KeyExtractor:
    """Extracts Widevine L1 credentials from Android devices."""

    # Common paths where Widevine keys might be stored
    WIDEVINE_PATHS = [
        "/data/misc/widevine/",
        "/data/media/widevine/",
        "/data/mediadrm/",
        "/cache/widevine/",
        "/persist/widevine/",
        "/data/data/com.widevine.app/",
        "/data/vendor/widevine/",
    ]

    CLIENT_ID_NAMES = [
        "client_id.bin",
        "clientid.bin",
        "widevine_client_id.bin",
    ]

    PRIVATE_KEY_NAMES = [
        "private_key.pem",
        "privatekey.pem",
        "widevine_key.pem",
        "private_key.key",
    ]

    def __init__(self, adb_handler: ADBHandler):
        """Initialize key extractor.
        
        Args:
            adb_handler: ADB handler instance.
        """
        self.adb = adb_handler
        self.key_parser = KeyParser()

    def find_keys(self) -> Tuple[Optional[str], Optional[str]]:
        """Find client_id.bin and private_key.pem on device.
        
        Returns:
            Tuple of (client_id_path, private_key_path) or (None, None) if not found.
        """
        logger.info("Searching for Widevine keys on device...")
        
        client_id_path = None
        private_key_path = None
        
        # Search in common paths
        for base_path in self.WIDEVINE_PATHS:
            logger.debug(f"Checking {base_path}")
            
            # Check if path exists
            output, rc = self.adb.shell(f"test -d {base_path} && echo 'exists'")
            if rc != 0 or "exists" not in output:
                continue
            
            # List files in directory
            output, rc = self.adb.shell(f"ls -la {base_path}")
            if rc != 0:
                continue
            
            # Look for client_id.bin
            if not client_id_path:
                for name in self.CLIENT_ID_NAMES:
                    if name in output:
                        potential_path = os.path.join(base_path, name)
                        if self._verify_file_readable(potential_path):
                            client_id_path = potential_path
                            logger.info(f"Found client_id.bin at: {client_id_path}")
                            break
            
            # Look for private_key.pem
            if not private_key_path:
                for name in self.PRIVATE_KEY_NAMES:
                    if name in output:
                        potential_path = os.path.join(base_path, name)
                        if self._verify_file_readable(potential_path):
                            private_key_path = potential_path
                            logger.info(f"Found private_key.pem at: {private_key_path}")
                            break
            
            if client_id_path and private_key_path:
                break
        
        # Try alternate method: find using find command
        if not client_id_path or not private_key_path:
            logger.info("Using find command to search for keys...")
            
            if not client_id_path:
                client_id_path = self._find_file_by_pattern("client_id.bin")
            
            if not private_key_path:
                private_key_path = self._find_file_by_pattern("private_key.pem")
        
        return client_id_path, private_key_path

    def _verify_file_readable(self, device_path: str) -> bool:
        """Verify file exists and is readable.
        
        Args:
            device_path: Path on device.
            
        Returns:
            True if file is readable, False otherwise.
        """
        output, rc = self.adb.shell(f"test -r {device_path} && echo 'readable'")
        return rc == 0 and "readable" in output

    def _find_file_by_pattern(self, filename: str) -> Optional[str]:
        """Find file on device using find command.
        
        Args:
            filename: Filename to search for.
            
        Returns:
            Path to file if found, None otherwise.
        """
        output, rc = self.adb.shell(f"find /data -name {filename} 2>/dev/null")
        if rc == 0 and output.strip():
            path = output.strip().split("\n")[0]
            if self._verify_file_readable(path):
                logger.info(f"Found {filename} at: {path}")
                return path
        
        return None

    def extract_keys(
        self,
        output_dir: str = "./widevine_keys"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Extract and dump Widevine keys.
        
        Args:
            output_dir: Directory to save extracted keys.
            
        Returns:
            Tuple of (success, client_id_path, private_key_path).
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Find keys on device
        client_id_device_path, private_key_device_path = self.find_keys()
        
        if not client_id_device_path and not private_key_device_path:
            logger.error("Could not find Widevine keys on device")
            return False, None, None
        
        success = True
        client_id_local_path = None
        private_key_local_path = None
        
        # Extract client_id.bin
        if client_id_device_path:
            client_id_local_path = os.path.join(output_dir, "client_id.bin")
            logger.info(f"Extracting client_id.bin...")
            if self.adb.pull(client_id_device_path, client_id_local_path):
                file_size = os.path.getsize(client_id_local_path)
                logger.info(f"✓ client_id.bin extracted successfully ({file_size} bytes)")
            else:
                logger.error(f"✗ Failed to extract client_id.bin")
                success = False
        else:
            logger.warning("client_id.bin not found on device")
        
        # Extract private_key.pem
        if private_key_device_path:
            private_key_local_path = os.path.join(output_dir, "private_key.pem")
            logger.info(f"Extracting private_key.pem...")
            if self.adb.pull(private_key_device_path, private_key_local_path):
                file_size = os.path.getsize(private_key_local_path)
                logger.info(f"✓ private_key.pem extracted successfully ({file_size} bytes)")
            else:
                logger.error(f"✗ Failed to extract private_key.pem")
                success = False
        else:
            logger.warning("private_key.pem not found on device")
        
        return success, client_id_local_path, private_key_local_path

    def verify_extracted_keys(
        self,
        client_id_path: Optional[str],
        private_key_path: Optional[str]
    ) -> bool:
        """Verify extracted key files.
        
        Args:
            client_id_path: Path to client_id.bin.
            private_key_path: Path to private_key.pem.
            
        Returns:
            True if keys are valid, False otherwise.
        """
        valid = True
        
        if client_id_path and os.path.exists(client_id_path):
            if os.path.getsize(client_id_path) > 0:
                logger.info(f"✓ client_id.bin verified (valid size)")
            else:
                logger.error(f"✗ client_id.bin is empty")
                valid = False
        
        if private_key_path and os.path.exists(private_key_path):
            if os.path.getsize(private_key_path) > 0:
                # Try to parse as PEM
                if self._verify_pem_format(private_key_path):
                    logger.info(f"✓ private_key.pem verified (valid PEM format)")
                else:
                    logger.warning(f"private_key.pem format verification failed")
            else:
                logger.error(f"✗ private_key.pem is empty")
                valid = False
        
        return valid

    def _verify_pem_format(self, filepath: str) -> bool:
        """Verify file is valid PEM format.
        
        Args:
            filepath: Path to file.
            
        Returns:
            True if valid PEM, False otherwise.
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                return "-----BEGIN" in content and "-----END" in content
        except Exception as e:
            logger.debug(f"PEM verification error: {e}")
            return False
