"""ADB device communication handler."""

import subprocess
import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class ADBHandler:
    """Manages ADB communication with Android devices."""

    def __init__(self, device_serial: Optional[str] = None):
        """Initialize ADB handler.
        
        Args:
            device_serial: Device serial number. If None, uses first available device.
        """
        self.device_serial = device_serial
        self._verify_adb_installed()

    @staticmethod
    def _verify_adb_installed() -> None:
        """Verify ADB is installed and accessible."""
        try:
            subprocess.run(["adb", "version"], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError(
                "ADB not found. Please install Android SDK Platform Tools or add ADB to PATH."
            )

    def get_devices(self) -> List[str]:
        """Get list of connected devices.
        
        Returns:
            List of device serial numbers.
        """
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            devices = []
            for line in result.stdout.split("\n")[1:]:
                if line.strip() and not line.startswith("List"):
                    parts = line.split()
                    if len(parts) > 1 and parts[1] == "device":
                        devices.append(parts[0])
            return devices
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list devices: {e}")
            return []

    def select_device(self) -> bool:
        """Select device if not already specified.
        
        Returns:
            True if device was selected, False otherwise.
        """
        if self.device_serial:
            return self._verify_device_connected()
        
        devices = self.get_devices()
        if not devices:
            logger.error("No devices found. Please connect an Android device.")
            return False
        
        if len(devices) == 1:
            self.device_serial = devices[0]
            logger.info(f"Selected device: {self.device_serial}")
            return True
        
        logger.info("Multiple devices found:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device}")
        
        choice = input("Select device (number): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(devices):
                self.device_serial = devices[idx]
                logger.info(f"Selected device: {self.device_serial}")
                return True
        except ValueError:
            pass
        
        logger.error("Invalid device selection")
        return False

    def _verify_device_connected(self) -> bool:
        """Verify selected device is connected.
        
        Returns:
            True if device is connected, False otherwise.
        """
        devices = self.get_devices()
        if self.device_serial in devices:
            return True
        
        logger.error(f"Device {self.device_serial} not found or not in 'device' state")
        return False

    def shell(self, command: str) -> Tuple[str, int]:
        """Execute shell command on device.
        
        Args:
            command: Shell command to execute.
            
        Returns:
            Tuple of (output, return_code).
        """
        if not self.device_serial:
            raise RuntimeError("No device selected")
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "shell", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return "", -1
        except Exception as e:
            logger.error(f"Error executing shell command: {e}")
            return "", -1

    def pull(self, device_path: str, local_path: str) -> bool:
        """Pull file from device.
        
        Args:
            device_path: Path on device.
            local_path: Local destination path.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.device_serial:
            raise RuntimeError("No device selected")
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "pull", device_path, local_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error pulling file: {e}")
            return False

    def push(self, local_path: str, device_path: str) -> bool:
        """Push file to device.
        
        Args:
            local_path: Local file path.
            device_path: Destination path on device.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.device_serial:
            raise RuntimeError("No device selected")
        
        try:
            result = subprocess.run(
                ["adb", "-s", self.device_serial, "push", local_path, device_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error pushing file: {e}")
            return False

    def get_device_info(self) -> dict:
        """Get device information.
        
        Returns:
            Dictionary with device properties.
        """
        info = {}
        properties = [
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.serialno",
            "ro.product.model",
            "ro.product.brand",
        ]
        
        for prop in properties:
            output, _ = self.shell(f"getprop {prop}")
            info[prop] = output.strip()
        
        return info
