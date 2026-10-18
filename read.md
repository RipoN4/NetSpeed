# Context & Goal
Build a cross-platform desktop Internet Speed Meter for Windows and macOS using Python 3 and PySide6. The app monitors real-time system-wide download and upload speeds every second without requiring administrator/root privileges.

# Key Features:
1. Dual Display Modes (User can switch via settings):
   - Mode A: Floating Desktop Widget
     - Frameless, translucent/semi-transparent background (75% opacity dark slate `#1E1E24`).
     - Draggable anywhere across monitors; persists saved coordinates in `config.json`.
     - "Always on top" toggleable.
   - Mode B: Native Bar Embed (Platform-specific):
     - On macOS: Uses PyObjC (`AppKit.NSStatusBar`) to display live text (`↓ X.X MB/s  ↑ Y.Y MB/s`) directly in the macOS Menu Bar.
     - On Windows: Uses the "TrafficMonitor technique" via `ctypes.windll.user32` to find the taskbar handle (`Shell_TrayWnd` / `TrayNotifyWnd`) and embed/dock a frameless mini-widget directly beside the taskbar system tray.
   - Mode C: Show Both simultaneously.

2. Minimalist UI:
   - Displays Upload (↑) and Download (↓) speeds.
   - Single-click or right-click context menu opens "Settings".

3. Settings Dialog:
   - Unit Format: Byte-based (B/s, KB/s, MB/s) vs Bit-based (bps, Kbps, Mbps).
   - Display Mode selection (Floating / Taskbar / Both).
   - Transparency/Opacity slider (for the floating widget).
   - "Launch on System Startup" toggle (writes to Windows registry `HKCU\...\Run` on Windows, or generates a LaunchAgent plist in `~/Library/LaunchAgents/` on macOS — no admin privileges required).

4. Bandwidth Sampling Engine:
   - Calculate speed in a dedicated `QThread` or `QTimer` using `psutil.net_io_counters()` every 1.0 second:
     Speed = (bytes_current - bytes_previous) / delta_time.

# Technical & File Structure Requirements:
Generate clean, production-grade code split across modular files:
- `main.py` (entry point, app loop, platform detection)
- `monitor.py` (bandwidth calculation worker thread)
- `overlay_widget.py` (draggable frameless desktop overlay)
- `win_taskbar.py` (Windows-specific Win32 API taskbar docking logic using ctypes)
- `mac_menubar.py` (macOS-specific NSStatusItem controller using PyObjC)
- `settings_dialog.py` (configuration modal and JSON persistence)
- `autostart.py` (cross-platform non-root startup integration)
- `requirements.txt`
- Complete instructions on how to run locally and how to package it into a standalone executable using PyInstaller.