"""
NETSpeed - Vector SVG Icons Module
Renders the custom download and upload SVG icons with dynamic color and sizing.
"""

from PySide6.QtCore import QByteArray, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QWidget

SVG_DOWNLOAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<path fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.0" d="m11.01 20.01l-6.77-6.77q-.99-.99.41-.99H7.1q1.4 0 1.4-1.4v-6.2q0-1.4 1.4-1.4h4.2q1.4 0 1.4 1.4v6.2q0 1.4 1.4 1.4h2.45q1.4 0 .41.99l-6.77 6.77q-.99.99-1.98 0"/>
</svg>"""

SVG_UPLOAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
<path fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.0" d="m12.99 3.99l6.77 6.77q.99.99-.41.99H16.9q-1.4 0-1.4 1.4v6.2q0 1.4-1.4 1.4H9.9q-1.4 0-1.4-1.4v-6.2q0-1.4-1.4-1.4H4.65q-1.4 0-.41-.99l6.77-6.77q.99-.99 1.98 0"/>
</svg>"""


class SvgArrowIcon(QWidget):
    """Custom SVG arrow icon widget supporting dynamic color and size."""
    def __init__(self, icon_type="down", color="#10B981", size=14, parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.color = color
        self.icon_size = size
        self.setFixedSize(size, size)
        self._renderer = None
        self._init_renderer()

    def _init_renderer(self):
        svg_template = SVG_DOWNLOAD if self.icon_type == "down" else SVG_UPLOAD
        svg_code = svg_template.format(color=self.color)
        self._renderer = QSvgRenderer(QByteArray(svg_code.encode("utf-8")))

    def set_size(self, size: int):
        self.icon_size = size
        self.setFixedSize(size, size)
        self.update()

    def set_color(self, color: str):
        self.color = color
        self._init_renderer()
        self.update()

    def paintEvent(self, event):
        if self._renderer and self._renderer.isValid():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self._renderer.render(painter, QRectF(0, 0, self.width(), self.height()))
