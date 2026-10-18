# NETSpeed ⚡

**By: RipoN**

A cross-platform desktop Internet Speed Meter for **Windows** and **macOS** built with **Python 3** and **PySide6**. The app monitors real-time system-wide download and upload speeds every second without requiring administrator or root privileges.

---

## 🌟 Key Features

### 1. Pure Plain Text Display with Custom SVG Icons
- Displays throughput as clean, minimalist plain text:
  $$\text{↓ X MB/s \ \ ↑ Y MB/s}$$
- **Zero background colors, zero boxes, zero borders, zero drop shadow effects**.
- High-contrast custom vector SVG icons:
  - Download Icon: `#10B981` (Neon Emerald Green)
  - Upload Icon: `#38BDF8` (Neon Sky Blue)
- Clean integer readouts without decimals (e.g., `↓ 2 KB/s  ↑ 2 KB/s`).
- Dynamic **Font Size** adjustment (9px to 24px) for high-DPI and custom display scaling.

### 2. Dual Display Modes
- **Taskbar (Mode B)**: Seamless plain text embedded directly into the Windows taskbar beside the clock and date (`TrayClockWClass`) / notification tray (`TrayNotifyWnd`).
  - **Supports ALL Windows versions (7, 8, 10, 11)**.
  - **Supports ALL taskbar alignments** (Bottom, Top, Left, Right).
- **Floating (Mode A)**: Pure plain text floating on your desktop, draggable across any monitor with persistent coordinates.
- **Both (Mode C)**: Shows on both the desktop HUD and native taskbar / menu bar simultaneously.

### 3. Native & Clean Settings Dialog
- Compact, native-styled system dialog (360 × 410 px):
  - **Display Mode**: `Taskbar`, `Floating`, `Both`
  - **Speed Unit**: `Bytes/Bits` (`Bytes`, `Bits`)
  - **Font Size**: Adjustable spinbox with real-time preview (9px to 24px)
  - **Options**: `Always On Top`, `Launch on Startup`
  - Native action buttons: `[ Center Widget ]`, `[ Cancel ]`, `[ Save ]`

### 4. Bandwidth Sampling Engine
- Runs in a dedicated background `QThread` (`BandwidthMonitor`) using `psutil.net_io_counters()` every 1.0 second:
  $$\text{Speed} = \frac{\text{Bytes}_{\text{current}} - \text{Bytes}_{\text{previous}}}{\Delta t}$$

---

## 📁 File Structure

```text
SpeedX/
├── main.py              # Entry point, app lifecycle, platform detection & coordination
├── monitor.py           # Bandwidth calculation worker thread (psutil delta loop)
├── overlay_widget.py    # Floating desktop HUD with custom SVG icons
├── win_taskbar.py       # Universal taskbar docking logic (beside clock)
├── mac_menubar.py       # macOS NSStatusItem controller using PyObjC
├── icons.py             # Custom SVG arrow icon renderer (QSvgRenderer)
├── settings_dialog.py   # Native preferences dialog (By: RipoN)
├── autostart.py         # Cross-platform non-root startup integration (Windows HKCU / macOS LaunchAgents)
├── config.py            # Local JSON settings persistence and integer unit formatting helpers
├── requirements.txt     # Python dependencies
├── SpeedX.spec          # PyInstaller cross-platform build specification
└── README.md            # Documentation and packaging guide
```

---

## 🚀 Running Locally

```powershell
# Standard execution
python main.py

# On Windows without a console window:
pythonw main.py
```

---

## 📦 Installation & Packaging

### Windows
1. **Standalone Portable Executable**:
   - Built output is located in [`dist/NETSpeed.exe`](file:///c:/Users/User/My%20Drive/2026/SpeedX/dist/NETSpeed.exe).
   - Fully standalone single-file binary with embedded icon, resources, and zero external dependencies.

2. **One-Click Installer (PowerShell)**:
   - Run [`Install-NETSpeed.ps1`](file:///c:/Users/User/My%20Drive/2026/SpeedX/Install-NETSpeed.ps1):
     ```powershell
     powershell -ExecutionPolicy Bypass -File Install-NETSpeed.ps1
     ```
   - Automatically installs to `%LOCALAPPDATA%\Programs\NETSpeed`, creates Start Menu and Desktop shortcuts with high-resolution icons, and launches the app.
   - To uninstall: `powershell -ExecutionPolicy Bypass -File Install-NETSpeed.ps1 -Uninstall`

3. **Inno Setup (Wizard Installer)**:
   - Compile [`installer_windows.iss`](file:///c:/Users/User/My%20Drive/2026/SpeedX/installer_windows.iss) with Inno Setup to produce `dist/NETSpeed-Setup.exe`.

4. **Portable ZIP Package**:
   - Ready-to-distribute archive: [`dist/NETSpeed-Windows-x64.zip`](file:///c:/Users/User/My%20Drive/2026/SpeedX/dist/NETSpeed-Windows-x64.zip).

---

### macOS
1. **Automated macOS Build Script**:
   - On any Mac, clone the repository and run:
     ```bash
     chmod +x build_mac.sh
     ./build_mac.sh
     ```
   - Generates `dist/NETSpeed.app` and a drag-and-drop installer disk image: `dist/NETSpeed-macOS.dmg`.

2. **Cloud Automated CI/CD (GitHub Actions)**:
   - A turnkey release pipeline is configured in [`.github/workflows/build-release.yml`](file:///c:/Users/User/My%20Drive/2026/SpeedX/.github/workflows/build-release.yml).
   - Pushing a version tag (e.g. `v1.0.0`) automatically compiles and uploads both `NETSpeed-Windows-x64.zip` and `NETSpeed-macOS.dmg` directly to GitHub Releases.

