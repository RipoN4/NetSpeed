"""
NETSpeed - Floating Desktop Overlay Widget
Displays pure plain text '↓ X MB/s  ↑ Y MB/s' with custom SVG icons,
configurable font size, and zero background boxes or effects.
"""

from pathlib import Path
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QColor, QPainter, QCursor, QFont, QIcon
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QMenu
)

import config
from icons import SvgArrowIcon


class OverlayWidget(QWidget):
    """
    Mode A: Pure plain text floating speed meter.
    Displays '↓ X MB/s  ↑ Y MB/s' on a transparent canvas without any boxes or background effects.
    Draggable anywhere across monitors; single-click opens Settings.
    """
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.config = cfg
        self._drag_pos = QPoint()
        self._click_start_pos = QPoint()
        self._is_dragging = False

        # Set Window Icon
        icon_path = Path(__file__).resolve().parent / "NetSpeed.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Window flags: Frameless, Tool window
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.config.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._init_ui()

        # Restore saved coordinates
        x = self.config.get("overlay_x", 120)
        y = self.config.get("overlay_y", 120)
        self.move(x, y)

    def _init_ui(self):
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        font_size = self.config.get("font_size", 12)
        icon_size = max(10, font_size + 2)

        # Download Section
        self.dl_icon = SvgArrowIcon(icon_type="down", color="#10B981", size=icon_size)
        self.dl_text = QLabel("0 KB/s")
        self.dl_text.setStyleSheet(f"""
            color: #FFFFFF;
            font-size: {font_size}px;
            font-weight: 600;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: transparent;
        """)

        # Upload Section
        self.ul_icon = SvgArrowIcon(icon_type="up", color="#38BDF8", size=icon_size)
        self.ul_text = QLabel("0 KB/s")
        self.ul_text.setStyleSheet(f"""
            color: #FFFFFF;
            font-size: {font_size}px;
            font-weight: 600;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: transparent;
        """)

        layout.addWidget(self.dl_icon)
        layout.addWidget(self.dl_text)
        layout.addSpacing(8)  # Exactly 8px clean gap
        layout.addWidget(self.ul_icon)
        layout.addWidget(self.ul_text)
        self.ul_label = self.ul_text

        self.adjustSize()

    def update_speeds(self, dl_val: str, dl_unit: str, ul_val: str, ul_unit: str):
        """Update live text values."""
        self.dl_text.setText(f"{dl_val} {dl_unit}")
        self.ul_text.setText(f"{ul_val} {ul_unit}")
        self.adjustSize()

    def update_config(self, cfg: dict):
        """Apply dynamic configuration changes (always on top, font size)."""
        self.config = cfg

        font_size = self.config.get("font_size", 12)
        icon_size = max(10, font_size + 2)

        self.dl_icon.set_size(icon_size)
        self.ul_icon.set_size(icon_size)

        style = f"""
            color: #FFFFFF;
            font-size: {font_size}px;
            font-weight: 600;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: transparent;
        """
        self.dl_text.setStyleSheet(style)
        self.ul_text.setStyleSheet(style)

        ontop = self.config.get("always_on_top", True)
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if ontop:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.adjustSize()
        self.update()

    def paintEvent(self, event):
        """Pure plain text: zero background box or border. Alpha=1 for hit-testing."""
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    # ==========================================
    # Mouse Drag & Click Handling
    # ==========================================
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._click_start_pos = event.globalPosition().toPoint()
            self._is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            if (current_pos - self._click_start_pos).manhattanLength() > 3:
                self._is_dragging = True
                self.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                self.move(current_pos - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if self._is_dragging:
                self._is_dragging = False
                self.config["overlay_x"] = self.x()
                self.config["overlay_y"] = self.y()
                config.save_config(self.config)
            else:
                self.settings_requested.emit()
            event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
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
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0078D4;
                color: #FFFFFF;
            }
        """)

        act_settings = menu.addAction("Settings")
        act_settings.triggered.connect(self.settings_requested.emit)

        menu.addSeparator()

        is_ontop = self.config.get("always_on_top", True)
        act_ontop = menu.addAction("Always on Top")
        act_ontop.setCheckable(True)
        act_ontop.setChecked(is_ontop)
        def _toggle_ontop():
            self.config["always_on_top"] = not is_ontop
            config.save_config(self.config)
            self.update_config(self.config)
        act_ontop.triggered.connect(_toggle_ontop)

        menu.addSeparator()

        act_exit = menu.addAction("Exit")
        act_exit.triggered.connect(self.exit_requested.emit)

        menu.exec(event.globalPos())
