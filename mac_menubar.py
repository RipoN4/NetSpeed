"""
SpeedX - macOS Menu Bar Controller
Uses PyObjC (AppKit.NSStatusBar) to embed a live text status item
directly into the macOS top Menu Bar (Mode B on macOS).
"""

import sys
from PySide6.QtCore import QObject, Signal

HAS_PYOBJC = False
if sys.platform == "darwin":
    try:
        from AppKit import (
            NSStatusBar, NSVariableStatusItemLength, NSMenu, NSMenuItem
        )
        from Foundation import NSObject
        HAS_PYOBJC = True
    except ImportError:
        HAS_PYOBJC = False


class MacMenuBarController(QObject):
    """
    Mode B (macOS): Native Menu Bar Embed using NSStatusBar.
    Displays live throughput string (e.g., '↓ 1.2 MB/s  ↑ 250 KB/s').
    """
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._status_item = None
        self._visible = False

        if HAS_PYOBJC:
            self._init_status_bar()

    def _init_status_bar(self):
        """Create NSStatusItem with dynamic length and attach context menu."""
        try:
            status_bar = NSStatusBar.systemStatusBar()
            self._status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)
            
            button = self._status_item.button()
            if button:
                button.setTitle_("SpeedX: Initializing...")

            # Context Menu
            menu = NSMenu.alloc().init()
            
            item_settings = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "SpeedX Settings...", "openSettings:", ""
            )
            item_settings.setTarget_(self)
            menu.addItem_(item_settings)

            menu.addItem_(NSMenuItem.separatorItem())

            item_quit = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Quit SpeedX", "quitApp:", "q"
            )
            item_quit.setTarget_(self)
            menu.addItem_(item_quit)

            self._status_item.setMenu_(menu)
        except Exception as e:
            print(f"[SpeedX Mac Menubar] Initialization error: {e}")

    def openSettings_(self, sender):
        """Callback from NSMenuItem."""
        self.settings_requested.emit()

    def quitApp_(self, sender):
        """Callback from NSMenuItem."""
        self.exit_requested.emit()

    def is_available(self) -> bool:
        """Return True if running on macOS with PyObjC available."""
        return HAS_PYOBJC and self._status_item is not None

    def update_speeds(self, dl_val: str, dl_unit: str, ul_val: str, ul_unit: str):
        """Update live text in the macOS Menu Bar."""
        if not self._status_item or not self._visible:
            return
        try:
            button = self._status_item.button()
            if button:
                text = f"↓ {dl_val} {dl_unit}  ↑ {ul_val} {ul_unit}"
                button.setTitle_(text)
        except Exception as e:
            print(f"[SpeedX Mac Menubar] Update error: {e}")

    def show(self):
        """Display the Menu Bar item."""
        self._visible = True
        if self._status_item:
            try:
                self._status_item.setVisible_(True)
            except Exception:
                pass

    def hide(self):
        """Hide the Menu Bar item."""
        self._visible = False
        if self._status_item:
            try:
                self._status_item.setVisible_(False)
            except Exception:
                pass
