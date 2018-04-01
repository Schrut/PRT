from PyQt5.QtWidgets import QLabel

from PyQt5.QtGui import (
    QPainter,
    QPaintEvent,
)

from PyQt5.QtCore import QRect

class RenderArea(QLabel):
    """ Create a "RenderArea" in which you
    can display mutiples QPixmap.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Stack of images (pixmaps) user wants to draw
        # tuples( pixmap, opacity of the pixmap, x coordinate, y coordinate )
        self.images = []

    def push_pixm(self, pixmap, opacity=1.0, x=0, y=0):
        """ Push a Pixmap + informations to the stack.
        """
        self.images.append((
            pixmap, 
            opacity, 
            x, 
            y
        ))

        # call the paintEvent function()
        self.update()

    def paintEvent(self, ev: QPaintEvent):
        painter = QPainter(self)
        images = self.images

        max_w = 0
        max_h = 0
        
        for _im in images:
            pixmap, opacity, _x, _y = _im

            painter.setOpacity(opacity)
            painter.drawPixmap(_x, _y, pixmap)

            _w = pixmap.width()
            _h = pixmap.height()

            if _w > max_w:
                max_w = _w
            
            if _h > max_h:
                max_h = _h
        
        self.setFixedSize(max_w, max_h)