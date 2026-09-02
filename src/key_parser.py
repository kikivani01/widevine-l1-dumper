"""Widevine key parsing and validation."""

import logging
import struct
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class KeyParser:
    """Parses and validates Widevine key files."""

    # Widevine client ID magic bytes
    CLIENT_ID_MAGIC = b"\x00\x00\x00\x00"

    def __init__(self):
        """Initialize key parser."""
        pass

    def parse_client_id(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse client_id.bin file.
        
        Args:
            filepath: Path to client_id.bin.
            
        Returns:
            Dictionary with parsed data or None if parsing fails.
        """
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            if len(data) < 4:
                logger.warning(f"client_id.bin too small: {len(data)} bytes")
                return None
            
            info = {
                "size": len(data),
                "hex_preview": data[:32].hex(),
                "ascii_preview": self._get_ascii_preview(data),
            }
            
            return info
        except Exception as e:
            logger.error(f"Error parsing client_id.bin: {e}")
            return None

    def parse_private_key(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Parse private_key.pem file.
        
        Args:
            filepath: Path to private_key.pem.
            
        Returns:
            Dictionary with parsed data or None if parsing fails.
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Validate PEM structure
            if "-----BEGIN" not in content or "-----END" not in content:
                logger.warning("Invalid PEM format")
                return None
            
            # Extract key type
            lines = content.split("\n")
            key_type = lines[0] if lines else "Unknown"
            
            info = {
                "size": len(content),
                "key_type": key_type,
                "line_count": len(lines),
                "valid_pem": True,
            }
            
            return info
        except Exception as e:
            logger.error(f"Error parsing private_key.pem: {e}")
            return None

    @staticmethod
    def _get_ascii_preview(data: bytes, length: int = 32) -> str:
        """Get ASCII preview of binary data.
        
        Args:
            data: Binary data.
            length: Number of bytes to preview.
            
        Returns:
            ASCII preview string.
        """
        preview = data[:length]
        return "".join(
            chr(b) if 32 <= b < 127 else "."
            for b in preview
        )

    def get_file_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Get general file information.
        
        Args:
            filepath: Path to file.
            
        Returns:
            Dictionary with file info or None.
        """
        try:
            path = Path(filepath)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "path": str(path),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode),
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
