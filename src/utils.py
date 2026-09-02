"""Utility functions for Widevine dumper."""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(verbose: bool = False, log_file: Optional[str] = None) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging.
        log_file: Optional log file path.
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    format_string = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        formatter = logging.Formatter(format_string)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)


def ensure_output_dir(output_dir: str) -> str:
    """Ensure output directory exists.
    
    Args:
        output_dir: Output directory path.
        
    Returns:
        Absolute path to output directory.
    """
    path = Path(output_dir).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def get_timestamp_str() -> str:
    """Get current timestamp as string.
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_backup_filename(original_name: str) -> str:
    """Get backup filename with timestamp.
    
    Args:
        original_name: Original filename.
        
    Returns:
        Filename with timestamp.
    """
    name, ext = os.path.splitext(original_name)
    return f"{name}_{get_timestamp_str()}{ext}"


def safe_delete_file(filepath: str) -> bool:
    """Safely delete a file.
    
    Args:
        filepath: Path to file.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception:
        pass
    return False


def bytes_to_hex(data: bytes, group_size: int = 16) -> str:
    """Convert bytes to formatted hex string.
    
    Args:
        data: Binary data.
        group_size: Bytes per line.
        
    Returns:
        Formatted hex string.
    """
    lines = []
    for i in range(0, len(data), group_size):
        chunk = data[i:i+group_size]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(
            chr(b) if 32 <= b < 127 else "."
            for b in chunk
        )
        lines.append(f"{i:08x}  {hex_part:<{group_size*3-1}}  {ascii_part}")
    return "\n".join(lines)
