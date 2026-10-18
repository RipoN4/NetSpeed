"""
NETSpeed - Settings Dialog Modal
Clean, native-styled preferences dialog for Windows and macOS.
Name: NETSpeed | RipoN
"""

from pathlib import Path
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QButtonGroup, QCheckBox, QPushButton, QGroupBox, QSpinBox, QMessageBox
)

import config
import autostart


def generate_ui_icons(output_dir: Path) -> dict:
    """Generate crisp, high-DPI vector icons for checkboxes and radio buttons."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "chk_on": output_dir / "chk_on.png",
        "chk_off": output_dir / "chk_off.png",
        "chk_hov": output_dir / "chk_hov.png",
        "rad_on": output_dir / "rad_on.png",
        "rad_off": output_dir / "rad_off.png",
        "rad_hov": output_dir / "rad_hov.png",
    }

    # 1. Checkbox Checked (18x18 equivalent rendered @ 36x36 for Retina/high-DPI)
    p_chk_on = QPixmap(36, 36)
    p_chk_on.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_chk_on)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#0078D4")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(QRectF(1, 1, 34, 34), 7, 7)
    pen = QPen(QColor("#FFFFFF"), 3.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    painter.drawLine(8, 18, 15, 25)
    painter.drawLine(15, 25, 27, 9)
    painter.end()
    p_chk_on.save(str(paths["chk_on"]), "PNG")

    # 2. Checkbox Unchecked
    p_chk_off = QPixmap(36, 36)
    p_chk_off.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_chk_off)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#1E1E1E")))
    painter.setPen(QPen(QColor("#666666"), 2.6))
    painter.drawRoundedRect(QRectF(2, 2, 32, 32), 7, 7)
    painter.end()
    p_chk_off.save(str(paths["chk_off"]), "PNG")

    # 3. Checkbox Hover
    p_chk_hov = QPixmap(36, 36)
    p_chk_hov.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_chk_hov)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#252525")))
    painter.setPen(QPen(QColor("#0078D4"), 2.6))
    painter.drawRoundedRect(QRectF(2, 2, 32, 32), 7, 7)
    painter.end()
    p_chk_hov.save(str(paths["chk_hov"]), "PNG")

    # 4. Radio Checked
    p_rad_on = QPixmap(36, 36)
    p_rad_on.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_rad_on)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#1E1E1E")))
    painter.setPen(QPen(QColor("#0078D4"), 2.8))
    painter.drawEllipse(QRectF(2, 2, 32, 32))
    painter.setBrush(QBrush(QColor("#0078D4")))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(10, 10, 16, 16))
    painter.end()
    p_rad_on.save(str(paths["rad_on"]), "PNG")

    # 5. Radio Unchecked
    p_rad_off = QPixmap(36, 36)
    p_rad_off.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_rad_off)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#1E1E1E")))
    painter.setPen(QPen(QColor("#666666"), 2.6))
    painter.drawEllipse(QRectF(2, 2, 32, 32))
    painter.end()
    p_rad_off.save(str(paths["rad_off"]), "PNG")

    # 6. Radio Hover
    p_rad_hov = QPixmap(36, 36)
    p_rad_hov.fill(Qt.GlobalColor.transparent)
    painter = QPainter(p_rad_hov)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(QColor("#252525")))
    painter.setPen(QPen(QColor("#0078D4"), 2.6))
    painter.drawEllipse(QRectF(2, 2, 32, 32))
    painter.end()
    p_rad_hov.save(str(paths["rad_hov"]), "PNG")

    return {k: v.as_posix() for k, v in paths.items()}


class SettingsDialog(QDialog):
    """Clean, native preferences dialog for NETSpeed."""
    config_changed = Signal(dict)

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.config = cfg

        self.setWindowTitle("NETSpeed Settings")
        self.setFixedSize(400, 580)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        icon_path = Path(__file__).resolve().parent / "NetSpeed.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._apply_native_styles()
        self._init_ui()

    def _apply_native_styles(self):
        icons = generate_ui_icons(config.get_config_dir())
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #202020;
                color: #FFFFFF;
                font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
                font-size: 13px;
            }}
            QGroupBox {{
                background-color: #282828;
                border: 1px solid #383838;
                border-radius: 8px;
                margin-top: 18px;
                padding-top: 14px;
                padding-left: 14px;
                padding-right: 14px;
                padding-bottom: 12px;
                font-weight: 600;
                color: #E0E0E0;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: #CCCCCC;
                background-color: #202020;
            }}
            QRadioButton, QCheckBox {{
                color: #FFFFFF;
                spacing: 10px;
                font-size: 13px;
                font-weight: normal;
                background: transparent;
                min-height: 26px;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                min-width: 18px;
                min-height: 18px;
            }}
            QRadioButton::indicator:unchecked {{
                image: url("{icons['rad_off']}");
            }}
            QRadioButton::indicator:unchecked:hover {{
                image: url("{icons['rad_hov']}");
            }}
            QRadioButton::indicator:checked {{
                image: url("{icons['rad_on']}");
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                min-width: 18px;
                min-height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url("{icons['chk_off']}");
            }}
            QCheckBox::indicator:unchecked:hover {{
                image: url("{icons['chk_hov']}");
            }}
            QCheckBox::indicator:checked {{
                image: url("{icons['chk_on']}");
            }}
            QSpinBox {{
                background-color: #282828;
                border: 1px solid #383838;
                border-radius: 6px;
                color: #FFFFFF;
                padding: 4px 10px;
                font-size: 13px;
                min-width: 85px;
                min-height: 26px;
            }}
            QSpinBox:focus {{
                border-color: #0078D4;
            }}
            QPushButton {{
                background-color: #303030;
                color: #FFFFFF;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 12px;
                font-weight: 500;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background-color: #3A3A3A;
                border-color: #555555;
            }}
            QPushButton:pressed {{
                background-color: #222222;
            }}
            QPushButton#SaveBtn {{
                background-color: #0078D4;
                border-color: #0078D4;
                font-weight: 600;
            }}
            QPushButton#SaveBtn:hover {{
                background-color: #1084D8;
            }}
        """)

    def _init_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(20, 16, 20, 18)
        vbox.setSpacing(10)

        # Header: App Icon + Name: NETSpeed | RipoN
        hdr_row = QHBoxLayout()
        hdr_row.setSpacing(12)

        icon_path = Path(__file__).resolve().parent / "NetSpeed.png"
        if icon_path.exists():
            logo_label = QLabel()
            pix = QPixmap(str(icon_path)).scaled(
                36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pix)
            hdr_row.addWidget(logo_label)

        hdr = QVBoxLayout()
        hdr.setSpacing(1)

        t = QLabel("NETSpeed")
        t.setStyleSheet("font-size: 20px; font-weight: 800; color: #FFFFFF;")
        by_label = QLabel("RipoN")
        by_label.setStyleSheet("font-size: 12px; color: #9CA3AF; font-weight: 500;")

        hdr.addWidget(t)
        hdr.addWidget(by_label)
        hdr_row.addLayout(hdr)
        hdr_row.addStretch()
        vbox.addLayout(hdr_row)

        # 1. Display Mode: Taskbar, Floating, Both
        grp_mode = QGroupBox("Display Mode")
        l_mode = QVBoxLayout(grp_mode)
        l_mode.setSpacing(8)

        self.radio_taskbar = QRadioButton("Taskbar")
        self.radio_floating = QRadioButton("Floating")
        self.radio_both = QRadioButton("Both")

        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_taskbar)
        self.mode_group.addButton(self.radio_floating)
        self.mode_group.addButton(self.radio_both)

        curr_mode = self.config.get("display_mode", "floating")
        if curr_mode == "taskbar":
            self.radio_taskbar.setChecked(True)
        elif curr_mode == "both":
            self.radio_both.setChecked(True)
        else:
            self.radio_floating.setChecked(True)

        l_mode.addWidget(self.radio_taskbar)
        l_mode.addWidget(self.radio_floating)
        l_mode.addWidget(self.radio_both)
        vbox.addWidget(grp_mode)

        # 2. Bytes/Bits Group
        grp_unit = QGroupBox("Bytes/Bits")
        l_unit = QHBoxLayout(grp_unit)
        l_unit.setSpacing(24)

        self.radio_bytes = QRadioButton("Bytes")
        self.radio_bits = QRadioButton("Bits")

        self.unit_group = QButtonGroup(self)
        self.unit_group.addButton(self.radio_bytes)
        self.unit_group.addButton(self.radio_bits)

        if self.config.get("unit_format") == "bits":
            self.radio_bits.setChecked(True)
        else:
            self.radio_bytes.setChecked(True)

        l_unit.addWidget(self.radio_bytes)
        l_unit.addWidget(self.radio_bits)
        l_unit.addStretch()
        vbox.addWidget(grp_unit)

        # 3. Font Size Option
        row_font = QHBoxLayout()
        lbl_font = QLabel("Font Size:")
        lbl_font.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 500;")

        self.spin_font = QSpinBox()
        self.spin_font.setRange(9, 24)
        self.spin_font.setValue(int(self.config.get("font_size", 12)))
        self.spin_font.setSuffix(" px")

        row_font.addWidget(lbl_font)
        row_font.addStretch()
        row_font.addWidget(self.spin_font)
        vbox.addLayout(row_font)

        # 4. Options Group: Always On Top, Launch on Startup
        grp_opt = QGroupBox("Options")
        l_opt = QVBoxLayout(grp_opt)
        l_opt.setSpacing(8)

        self.chk_ontop = QCheckBox("Always On Top")
        self.chk_ontop.setChecked(self.config.get("always_on_top", True))

        self.chk_startup = QCheckBox("Launch on Startup")
        self.chk_startup.setChecked(autostart.is_autostart_enabled())

        l_opt.addWidget(self.chk_ontop)
        l_opt.addWidget(self.chk_startup)
        vbox.addWidget(grp_opt)

        vbox.addStretch()

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        btn_center = QPushButton("Center Widget")
        btn_center.clicked.connect(self._center_widget)
        btn_bar.addWidget(btn_center)

        btn_bar.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_bar.addWidget(btn_cancel)

        btn_save = QPushButton("Save")
        btn_save.setObjectName("SaveBtn")
        btn_save.clicked.connect(self._save_and_apply)
        btn_bar.addWidget(btn_save)

        vbox.addLayout(btn_bar)

    def _center_widget(self):
        screen = self.screen().geometry()
        self.config["overlay_x"] = (screen.width() - 110) // 2
        self.config["overlay_y"] = (screen.height() - 24) // 2
        config.save_config(self.config)
        self.config_changed.emit(self.config)

    def _save_and_apply(self):
        # 1. Display Mode: Taskbar, Floating, Both
        if self.radio_taskbar.isChecked():
            self.config["display_mode"] = "taskbar"
        elif self.radio_both.isChecked():
            self.config["display_mode"] = "both"
        else:
            self.config["display_mode"] = "floating"

        # 2. Unit format: Bytes / Bits
        self.config["unit_format"] = "bits" if self.radio_bits.isChecked() else "bytes"

        # 3. Font size
        self.config["font_size"] = self.spin_font.value()

        # 4. Always On Top
        self.config["always_on_top"] = self.chk_ontop.isChecked()

        # 5. Launch on Startup
        want_startup = self.chk_startup.isChecked()
        success = autostart.set_autostart(want_startup)
        if not success:
            QMessageBox.warning(self, "Startup Error", "Could not update startup registry or agent.")
        self.config["autostart"] = want_startup

        config.save_config(self.config)
        self.config_changed.emit(self.config)
        self.accept()
