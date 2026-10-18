"""
NETSpeed - Configuration & Unit Formatting Module
Handles persistent settings stored in QStandardPaths.AppDataLocation and
provides high-precision unit conversions without decimal places.
"""

import json
import os
import sys
from pathlib import Path
from PySide6.QtCore import QStandardPaths

CONFIG_FILENAME = "config.json"
APP_NAME = "NETSpeed"
AUTHOR = "RipoN"

DEFAULT_CONFIG = {
    "display_mode": "both",       # "taskbar", "floating", "both"
    "unit_format": "bytes",       # "bytes" or "bits"
    "font_size": 12,              # 10, 11, 12, 13, 14, 16, 18, 20 px
    "always_on_top": True,
    "overlay_x": 100,
    "overlay_y": 100,
    "taskbar_offset": 0,          # Dynamic offset along taskbar
    "autostart": False
}


def get_config_dir() -> Path:
    """Return the platform-appropriate AppData configuration directory."""
    try:
        app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not app_data:
            app_data = str(Path.home() / ".netspeed")
    except Exception:
        app_data = str(Path.home() / ".netspeed")
    
    config_dir = Path(app_data)
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file_path() -> Path:
    """Get the full path to config.json."""
    return get_config_dir() / CONFIG_FILENAME


def load_config() -> dict:
    """Load configuration from disk, falling back to default values."""
    config = dict(DEFAULT_CONFIG)
    config_path = get_config_file_path()

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    config.update(saved)
        except Exception as e:
            print(f"[NETSpeed] Warning: Could not read config file ({e}). Using defaults.")

    return config


def save_config(config_data: dict) -> bool:
    """Persist configuration to disk safely."""
    config_path = get_config_file_path()
    try:
        tmp_path = config_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
        
        # Atomic replace
        if sys.platform == "win32" and config_path.exists():
            config_path.unlink()
        tmp_path.rename(config_path)
        return True
    except Exception as e:
        print(f"[NETSpeed] Error saving config: {e}")
        return False


def format_speed(bytes_per_sec: float, unit_format: str = "bytes") -> tuple[str, str]:
    """
    Format raw bytes/sec into clean integer (value, unit) with ZERO decimal places.
    
    - Byte-based: B/s, KB/s, MB/s, GB/s (1024 base)
    - Bit-based:  bps, Kbps, Mbps, Gbps (bits = bytes * 8, 1000 base)
    """
    if bytes_per_sec <= 0:
        return "0", ("B/s" if unit_format == "bytes" else "bps")

    if unit_format == "bits":
        bits_per_sec = bytes_per_sec * 8.0
        if bits_per_sec < 1_000:
            return f"{round(bits_per_sec)}", "bps"
        elif bits_per_sec < 1_000_000:
            val = round(bits_per_sec / 1e3)
            return f"{val}", "Kbps"
        elif bits_per_sec < 1_000_000_000:
            val = round(bits_per_sec / 1e6)
            return f"{val}", "Mbps"
        else:
            val = round(bits_per_sec / 1e9)
            return f"{val}", "Gbps"
    else:
        # Byte-based (default)
        if bytes_per_sec < 1024:
            return f"{round(bytes_per_sec)}", "B/s"
        elif bytes_per_sec < 1024 * 1024:
            val = round(bytes_per_sec / 1024.0)
            return f"{val}", "KB/s"
        elif bytes_per_sec < 1024 * 1024 * 1024:
            val = round(bytes_per_sec / (1024.0 ** 2))
            return f"{val}", "MB/s"
        else:
            val = round(bytes_per_sec / (1024.0 ** 3))
            return f"{val}", "GB/s"
