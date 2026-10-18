"""
SpeedX - Main Application Entry Point & Orchestrator
Coordinates platform detection, dual display modes (Floating Overlay & Native Bar Embed),
bandwidth monitoring thread, and settings persistence.
"""

import sys
import io

# Safe stdout/stderr handling for windowed PyInstaller executables (console=False)
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

import config
from monitor import BandwidthMonitor
from overlay_widget import OverlayWidget
from settings_dialog import SettingsDialog

# Platform-specific native bar embeds
if sys.platform == "win32":
    from win_taskbar import WinTaskbarWidget
else:
    WinTaskbarWidget = None

if sys.platform == "darwin":
    from mac_menubar import MacMenuBarController
else:
    MacMenuBarController = None


from pathlib import Path


def generate_tray_icon() -> QIcon:
    """Return the official high-resolution NetSpeed icon."""
    base_dir = Path(__file__).resolve().parent
    png_path = base_dir / "NetSpeed.png"
    if png_path.exists():
        return QIcon(str(png_path))
    ico_path = base_dir / "NetSpeed.ico"
    if ico_path.exists():
        return QIcon(str(ico_path))

    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#1A1A22")))
    painter.setPen(QPen(QColor("#38BDF8"), 1.8))
    painter.drawRoundedRect(2, 2, 28, 28, 7, 7)
    painter.end()
    return QIcon(pixmap)


class SpeedXApp:
    """Core coordinator for SpeedX."""

    def __init__(self):
        self.config = config.load_config()

        # 1. UI Components
        self.overlay_widget = OverlayWidget(self.config)
        self.settings_dialog = None

        # Platform specific widgets
        self.win_taskbar_widget = None
        self.mac_menubar_controller = None

        if sys.platform == "win32" and WinTaskbarWidget:
            self.win_taskbar_widget = WinTaskbarWidget(self.config)

        if sys.platform == "darwin" and MacMenuBarController:
            self.mac_menubar_controller = MacMenuBarController()

        # 2. System Tray Icon (Fallback anchor)
        self._init_tray()

        # 3. Bandwidth Monitoring Engine (Dedicated QThread)
        self.monitor = BandwidthMonitor(interval=1.0, unit_format=self.config.get("unit_format", "bytes"))
        self.monitor.speed_updated.connect(self._on_speed_updated)
        self.monitor.start()

        # 4. Connect Signals
        self._connect_signals()

        # 5. Apply initial display mode
        self._apply_display_mode()

    def _init_tray(self):
        self.tray = QSystemTrayIcon(generate_tray_icon())
        self.tray.setToolTip("NETSpeed - RipoN")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #202020;
                color: #FFFFFF;
                border: 1px solid #383838;
                border-radius: 6px;
                padding: 4px;
                font-family: 'Segoe UI', system-ui, sans-serif;
                font-size: 12px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
        """)

        act_settings = menu.addAction("Settings")
        act_settings.triggered.connect(self._open_settings)

        menu.addSeparator()

        act_quit = menu.addAction("Exit")
        act_quit.triggered.connect(self._quit_app)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _connect_signals(self):
        # Overlay
        self.overlay_widget.settings_requested.connect(self._open_settings)
        self.overlay_widget.exit_requested.connect(self._quit_app)

        # Windows Taskbar
        if self.win_taskbar_widget:
            self.win_taskbar_widget.settings_requested.connect(self._open_settings)
            self.win_taskbar_widget.exit_requested.connect(self._quit_app)

        # macOS Menubar
        if self.mac_menubar_controller:
            self.mac_menubar_controller.settings_requested.connect(self._open_settings)
            self.mac_menubar_controller.exit_requested.connect(self._quit_app)

    def _on_speed_updated(self, dl_raw, ul_raw, dl_val, dl_unit, ul_val, ul_unit):
        """Dispatch bandwidth data to all active display modes."""
        mode = self.config.get("display_mode", "floating")

        # Mode A: Floating Overlay
        if mode in ("floating", "both"):
            if self.overlay_widget.isVisible():
                self.overlay_widget.update_speeds(dl_val, dl_unit, ul_val, ul_unit)

        # Mode B: Native Bar Embed
        if mode in ("taskbar", "both"):
            if sys.platform == "win32" and self.win_taskbar_widget:
                if self.win_taskbar_widget.isVisible():
                    self.win_taskbar_widget.update_speeds(dl_val, dl_unit, ul_val, ul_unit)
            elif sys.platform == "darwin" and self.mac_menubar_controller:
                self.mac_menubar_controller.update_speeds(dl_val, dl_unit, ul_val, ul_unit)

        # Tray Tooltip
        self.tray.setToolTip(f"NETSpeed by RipoN\n↓ {dl_val} {dl_unit}\n↑ {ul_val} {ul_unit}")

    def _apply_display_mode(self):
        """Toggle visibility according to active display mode (Floating / Taskbar / Both)."""
        mode = self.config.get("display_mode", "floating")

        # 1. Floating Overlay
        if mode in ("floating", "both"):
            self.overlay_widget.show()
        else:
            self.overlay_widget.hide()

        # 2. Native Bar Embed
        if mode in ("taskbar", "both"):
            if sys.platform == "win32" and self.win_taskbar_widget:
                self.win_taskbar_widget.reposition_to_taskbar()
                self.win_taskbar_widget.show()
            elif sys.platform == "darwin" and self.mac_menubar_controller:
                self.mac_menubar_controller.show()
        else:
            if sys.platform == "win32" and self.win_taskbar_widget:
                self.win_taskbar_widget.hide()
            elif sys.platform == "darwin" and self.mac_menubar_controller:
                self.mac_menubar_controller.hide()

    def _open_settings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.config)
            self.settings_dialog.config_changed.connect(self._on_config_changed)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def _on_config_changed(self, new_config: dict):
        self.config = new_config
        # Update monitor unit format
        self.monitor.set_unit_format(self.config.get("unit_format", "bytes"))
        # Update overlay widget appearance & font size
        self.overlay_widget.update_config(self.config)
        # Update taskbar widget appearance & font size
        if self.win_taskbar_widget:
            self.win_taskbar_widget.update_config(self.config)
        # Apply display mode changes
        self._apply_display_mode()

    def _on_tray_activated(self, reason):
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick
        ):
            self._open_settings()

    def _quit_app(self):
        # Save overlay position
        if self.overlay_widget.isVisible():
            self.config["overlay_x"] = self.overlay_widget.x()
            self.config["overlay_y"] = self.overlay_widget.y()
            config.save_config(self.config)

        self.monitor.stop()
        self.monitor.wait(1000)
        self.tray.hide()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NETSpeed")
    app.setApplicationDisplayName("NETSpeed")
    app.setOrganizationName("RipoN")
    app.setQuitOnLastWindowClosed(False)

    app_icon = generate_tray_icon()
    app.setWindowIcon(app_icon)

    speedx = SpeedXApp()
    cfg = speedx.config
    try:
        if sys.stdout is not None:
            print("=" * 48)
            print("  NETSpeed by RipoN - Started")
            print(f"  Mode: {cfg.get('display_mode', 'both')} | Units: {cfg.get('unit_format', 'bytes')} | Font: {cfg.get('font_size', 12)}px")
            print("  Right-click or click meter / system tray for Settings.")
            print("=" * 48)
            if hasattr(sys.stdout, "flush") and callable(sys.stdout.flush):
                sys.stdout.flush()
    except Exception:
        pass

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
