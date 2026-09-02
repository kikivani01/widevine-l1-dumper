"""Widevine client utilities."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WidevineClient:
    """Widevine client information and utilities."""

    def __init__(self, client_id: bytes, private_key: bytes):
        """Initialize Widevine client.
        
        Args:
            client_id: Client ID binary data.
            private_key: Private key data.
        """
        self.client_id = client_id
        self.private_key = private_key

    def get_client_id_hex(self) -> str:
        """Get client ID as hex string.
        
        Returns:
            Hex representation of client ID.
        """
        return self.client_id.hex() if self.client_id else ""

    def get_info(self) -> Dict[str, Any]:
        """Get client information.
        
        Returns:
            Dictionary with client info.
        """
        return {
            "client_id_size": len(self.client_id) if self.client_id else 0,
            "private_key_size": len(self.private_key) if self.private_key else 0,
        }
