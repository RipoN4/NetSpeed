"""
NETSpeed - Windows Taskbar Dynamic Docking Module
Universal Windows Taskbar Integration supporting ALL Windows versions (7, 8, 10, 11).
Displays pure plain text '↓ X MB/s  ↑ Y MB/s' dynamically positioned in the available space
beside system tray icons & clock, adjusting automatically when icons are added or removed.
Supports interactive dragging to fine-tune placement along the taskbar.
"""

import sys
import ctypes
from ctypes import wintypes
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QColor, QPainter, QCursor, QIcon
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QMenu, QApplication
)

import config
from icons import SvgArrowIcon

# Win32 Constants
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
HWND_TOPMOST = -1

# AppBar Edge Constants
ABE_LEFT = 0
ABE_TOP = 1
ABE_RIGHT = 2
ABE_BOTTOM = 3
ABM_GETTASKBARPOS = 5

# Window Styles
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008


class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]


if sys.platform == "win32":
    user32 = ctypes.windll.user32
    shell32 = ctypes.windll.shell32
    kernel32 = ctypes.windll.kernel32

    user32.SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
        wintypes.UINT
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND

    user32.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowExW.restype = wintypes.HWND

    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL

    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL

    shell32.SHAppBarMessage.argtypes = [wintypes.DWORD, ctypes.c_void_p]
    shell32.SHAppBarMessage.restype = ctypes.c_ulonglong


class WinTaskbarWidget(QWidget):
    """
    Mode B (Windows): Native Taskbar Embedded Speed Meter.
    Displays pure plain text '↓ X MB/s  ↑ Y MB/s' tightly packed in the taskbar.
    Dynamically adapts position based on available space and icons count beside date and time.
    """
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        self.config = cfg
        self._current_edge = ABE_BOTTOM
        self._last_target_box = None

        # Drag state
        self._is_dragging = False
        self._drag_start_pos = QPoint()
        self._drag_start_offset = 0

        # Set Window Icon
        icon_path = Path(__file__).resolve().parent / "NetSpeed.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Window Flags: Frameless, Tool Window, Always on Top, Non-activating
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._init_ui()
        self._apply_win32_styles()

        # Immediate position calculation
        self.reposition_to_taskbar()

        # Anchor tracking timer (dynamic re-measurement of tray & icons)
        self._anchor_timer = QTimer(self)
        self._anchor_timer.setInterval(500)
        self._anchor_timer.timeout.connect(self.reposition_to_taskbar)
        self._anchor_timer.start()

    def _init_ui(self):
        """Construct tightly packed plain text layout with exact 8px spacing."""
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip("NETSpeed - Click for Settings | Drag to reposition on Taskbar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(4)

        font_size = self.config.get("font_size", 12)
        icon_size = max(10, font_size + 1)

        # Download Part
        self.dl_icon = SvgArrowIcon(icon_type="down", color="#10B981", size=icon_size)
        self.dl_label = QLabel("0 KB/s")
        self.dl_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {font_size}px; font-weight: 600; "
            f"font-family: 'Segoe UI', system-ui, sans-serif; background: transparent;"
        )

        # Upload Part
        self.ul_icon = SvgArrowIcon(icon_type="up", color="#38BDF8", size=icon_size)
        self.ul_label = QLabel("0 KB/s")
        self.ul_label.setStyleSheet(
            f"color: #FFFFFF; font-size: {font_size}px; font-weight: 600; "
            f"font-family: 'Segoe UI', system-ui, sans-serif; background: transparent;"
        )

        layout.addWidget(self.dl_icon)
        layout.addWidget(self.dl_label)
        layout.addSpacing(8)  # Exactly 8px clean gap
        layout.addWidget(self.ul_icon)
        layout.addWidget(self.ul_label)

        self.adjustSize()

    def _apply_win32_styles(self):
        if sys.platform != "win32":
            return
        try:
            hwnd = int(self.winId())
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style |= (WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"[NETSpeed Taskbar] Win32 style note: {e}")

    def update_speeds(self, dl_val: str, dl_unit: str, ul_val: str, ul_unit: str):
        """Update live text values."""
        self.dl_label.setText(f"{dl_val} {dl_unit}")
        self.ul_label.setText(f"{ul_val} {ul_unit}")
        self.adjustSize()
        self.reposition_to_taskbar()

    def update_config(self, cfg: dict):
        """Update font size and icon size dynamically from settings."""
        self.config = cfg
        font_size = self.config.get("font_size", 12)
        icon_size = max(10, font_size + 1)

        self.dl_icon.set_size(icon_size)
        self.ul_icon.set_size(icon_size)

        style = (
            f"color: #FFFFFF; font-size: {font_size}px; font-weight: 600; "
            f"font-family: 'Segoe UI', system-ui, sans-serif; background: transparent;"
        )
        self.dl_label.setStyleSheet(style)
        self.ul_label.setStyleSheet(style)

        self.adjustSize()
        self.reposition_to_taskbar()

    def _detect_taskbar_geometry(self):
        """
        Dynamically scan Windows Taskbar hierarchy across Windows 7, 8, 10, and 11.
        Returns:
            edge: ABE_BOTTOM, ABE_TOP, ABE_LEFT, ABE_RIGHT
            t_rect: (left, top, right, bottom) of taskbar
            leftmost_tray_x: leftmost coordinate of system tray / icons / clock
            topmost_tray_y: topmost coordinate of system tray (for vertical taskbars)
            rightmost_app_x: rightmost edge of running app buttons / start
        """
        edge = ABE_BOTTOM
        t_rect = (0, 0, 0, 0)
        h_tray = 0

        try:
            # Attach to default desktop if available
            hdesk = user32.OpenDesktopW("default", 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)

            h_tray = user32.FindWindowW("Shell_TrayWnd", 0)
            if not h_tray:
                h_tray = user32.FindWindowW("Shell_SecondaryTrayWnd", 0)

            if h_tray:
                r = wintypes.RECT()
                if user32.GetWindowRect(h_tray, ctypes.byref(r)):
                    t_w = r.right - r.left
                    t_h = r.bottom - r.top
                    t_rect = (r.left, r.top, r.right, r.bottom)
                    if t_w > t_h:
                        edge = ABE_TOP if r.top <= 0 else ABE_BOTTOM
                    else:
                        edge = ABE_LEFT if r.left <= 0 else ABE_RIGHT
        except Exception:
            pass

        # Fallback to SHAppBarMessage
        if t_rect == (0, 0, 0, 0):
            try:
                abd = APPBARDATA()
                abd.cbSize = ctypes.sizeof(APPBARDATA)
                if shell32.SHAppBarMessage(ABM_GETTASKBARPOS, ctypes.byref(abd)):
                    edge = abd.uEdge
                    t_rect = (abd.rc.left, abd.rc.top, abd.rc.right, abd.rc.bottom)
            except Exception:
                pass

        # Fallback to Qt Primary Screen Geometry
        if t_rect == (0, 0, 0, 0):
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                if screen:
                    g = screen.geometry()
                    a = screen.availableGeometry()
                    if a.top() > g.top():
                        edge = ABE_TOP
                        t_rect = (g.left(), g.top(), g.right(), a.top())
                    elif a.left() > g.left():
                        edge = ABE_LEFT
                        t_rect = (g.left(), g.top(), a.left(), g.bottom())
                    elif a.right() < g.right():
                        edge = ABE_RIGHT
                        t_rect = (a.right(), g.top(), g.right(), g.bottom())
                    else:
                        edge = ABE_BOTTOM
                        t_rect = (g.left(), a.bottom(), g.right(), g.bottom())

        t_left, t_top, t_right, t_bottom = t_rect
        t_width = max(1, t_right - t_left)
        t_height = max(1, t_bottom - t_top)
        is_horizontal = t_width >= t_height

        leftmost_tray_x = t_right
        topmost_tray_y = t_bottom
        rightmost_app_x = t_left

        # Dynamically scan children of Shell_TrayWnd to find real bounds of tray icons & apps
        if h_tray:
            try:
                def enum_proc(hwnd, lparam):
                    nonlocal leftmost_tray_x, topmost_tray_y, rightmost_app_x
                    if not user32.IsWindowVisible(hwnd):
                        return True
                    r = wintypes.RECT()
                    if not user32.GetWindowRect(hwnd, ctypes.byref(r)):
                        return True
                    w = r.right - r.left
                    h = r.bottom - r.top
                    if w <= 0 or h <= 0:
                        return True

                    cls = ctypes.create_unicode_buffer(256)
                    user32.GetClassNameW(hwnd, cls, 256)
                    name = cls.value

                    # 1. System Tray / Notification / Clock Elements
                    is_tray_element = False
                    if any(k in name for k in [
                        "TrayNotifyWnd", "SysPager", "ToolbarWindow32", "TrayClockWClass",
                        "TrayInputIndicatorWClass", "InputIndicatorButton", "TrayButton",
                        "TrayShowDesktopButtonWClass", "Windows.UI.Input.InputSite",
                        "Clock", "Notification", "ExperienceHost"
                    ]):
                        if is_horizontal and r.left >= t_left + (t_width // 4):
                            is_tray_element = True
                        elif not is_horizontal and r.top >= t_top + (t_height // 4):
                            is_tray_element = True

                    if is_tray_element:
                        if is_horizontal and r.left < leftmost_tray_x and r.left > t_left:
                            leftmost_tray_x = r.left
                        if not is_horizontal and r.top < topmost_tray_y and r.top > t_top:
                            topmost_tray_y = r.top

                    # 2. Running Applications / Task List Elements
                    elif any(k in name for k in [
                        "MSTaskListWClass", "MSTaskSwWClass", "TaskListButtonPanel", "Start"
                    ]):
                        if is_horizontal and r.right > rightmost_app_x and r.right < t_right:
                            rightmost_app_x = r.right

                    return True

                EnumChildProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
                user32.EnumChildWindows(h_tray, EnumChildProc(enum_proc), 0)
            except Exception:
                pass

        # Safe defaults if no tray window found
        if leftmost_tray_x >= t_right:
            leftmost_tray_x = t_right - 260
        if topmost_tray_y >= t_bottom:
            topmost_tray_y = t_bottom - 200

        return edge, t_rect, leftmost_tray_x, topmost_tray_y, rightmost_app_x

    def reposition_to_taskbar(self):
        """Align widget dynamically beside tray icons, adapting to available space."""
        if sys.platform != "win32":
            return
        if self._is_dragging:
            return  # User is actively dragging, don't overwrite position

        edge, (t_left, t_top, t_right, t_bottom), leftmost_tray_x, topmost_tray_y, rightmost_app_x = (
            self._detect_taskbar_geometry()
        )
        self._current_edge = edge

        t_width = max(1, t_right - t_left)
        t_height = max(1, t_bottom - t_top)

        # Dynamic tight width derived from text sizeHint + 4px margin
        target_w = max(self.sizeHint().width() + 4, 80)
        target_h = max(20, min(t_height - 4, 32))
        self.setFixedSize(target_w, target_h)

        user_offset = self.config.get("taskbar_offset", 0)

        # Calculate dynamic position based on available space
        if edge in (ABE_BOTTOM, ABE_TOP):
            # Anchor 6px to the left of the leftmost tray icon
            base_x = leftmost_tray_x - target_w - 6
            target_x = base_x + user_offset

            # Clamp so it never overlaps past the right screen edge or running apps
            min_x = max(t_left + 48, rightmost_app_x + 6) if rightmost_app_x > t_left else (t_left + 48)
            max_x = t_right - target_w - 10
            target_x = max(min_x, min(target_x, max_x))

            # Vertically center in taskbar
            target_y = t_top + max(0, (t_height - target_h) // 2)

        elif edge == ABE_LEFT:
            target_x = t_left + max(2, (t_width - target_w) // 2)
            base_y = topmost_tray_y - target_h - 6
            target_y = max(t_top + 48, min(base_y + user_offset, t_bottom - target_h - 10))

        elif edge == ABE_RIGHT:
            target_x = t_left + max(2, (t_width - target_w) // 2)
            base_y = topmost_tray_y - target_h - 6
            target_y = max(t_top + 48, min(base_y + user_offset, t_bottom - target_h - 10))

        else:
            base_x = leftmost_tray_x - target_w - 6
            target_x = base_x + user_offset
            target_y = t_top + max(0, (t_height - target_h) // 2)

        target_box = (target_x, target_y, target_w, target_h)
        if target_box != self._last_target_box:
            self._last_target_box = target_box
            self.setGeometry(target_x, target_y, target_w, target_h)
            try:
                hwnd = int(self.winId())
                user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    target_x,
                    target_y,
                    target_w,
                    target_h,
                    SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
            except Exception as e:
                print(f"[NETSpeed Taskbar] Win32 SetWindowPos note: {e}")

    def paintEvent(self, event):
        """Pure plain text: zero background box or border. Alpha=1 for hit-testing."""
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 1))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint()
            self._drag_start_offset = self.config.get("taskbar_offset", 0)
            self._drag_moved = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging:
            cur_pos = event.globalPosition().toPoint()
            dx = cur_pos.x() - self._drag_start_pos.x()
            dy = cur_pos.y() - self._drag_start_pos.y()

            if abs(dx) > 3 or abs(dy) > 3:
                self._drag_moved = True

            # Adjust horizontal or vertical offset based on edge
            if self._current_edge in (ABE_BOTTOM, ABE_TOP):
                new_offset = self._drag_start_offset + dx
            else:
                new_offset = self._drag_start_offset + dy

            self.config["taskbar_offset"] = new_offset

            # Re-position immediately while dragging
            edge, (t_left, t_top, t_right, t_bottom), leftmost_tray_x, topmost_tray_y, rightmost_app_x = (
                self._detect_taskbar_geometry()
            )
            target_w = self.width()
            target_h = self.height()
            t_height = max(1, t_bottom - t_top)

            if edge in (ABE_BOTTOM, ABE_TOP):
                base_x = leftmost_tray_x - target_w - 6
                target_x = base_x + new_offset
                min_x = max(t_left + 48, rightmost_app_x + 6) if rightmost_app_x > t_left else (t_left + 48)
                max_x = t_right - target_w - 10
                target_x = max(min_x, min(target_x, max_x))
                target_y = t_top + max(0, (t_height - target_h) // 2)
            else:
                target_x = t_left + max(2, (t_right - t_left - target_w) // 2)
                base_y = topmost_tray_y - target_h - 6
                target_y = max(t_top + 48, min(base_y + new_offset, t_bottom - target_h - 10))

            self.setGeometry(target_x, target_y, target_w, target_h)
            try:
                hwnd = int(self.winId())
                user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    target_x,
                    target_y,
                    target_w,
                    target_h,
                    SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
            except Exception:
                pass
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            was_dragging = self._is_dragging
            moved = getattr(self, "_drag_moved", False)
            self._is_dragging = False

            if moved:
                # Save the new offset
                config.save_config(self.config)
            else:
                # Quick click opens settings
                self.settings_requested.emit()
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Double click resets offset to 0 (auto-snap)
            self.config["taskbar_offset"] = 0
            config.save_config(self.config)
            self.reposition_to_taskbar()
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

        icon_path = Path(__file__).resolve().parent / "NetSpeed.png"
        app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()

        act_settings = menu.addAction(app_icon, "Settings")
        act_settings.triggered.connect(self.settings_requested.emit)

        act_reset = menu.addAction("Reset Position (Auto-Snap)")
        def _reset_pos():
            self.config["taskbar_offset"] = 0
            config.save_config(self.config)
            self.reposition_to_taskbar()
        act_reset.triggered.connect(_reset_pos)

        menu.addSeparator()

        act_exit = menu.addAction("Exit")
        act_exit.triggered.connect(self.exit_requested.emit)

        menu.exec(event.globalPos())
