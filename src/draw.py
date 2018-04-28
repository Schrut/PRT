from PyQt5.QtWidgets import QLabel

from PyQt5.QtGui import (
    QPainter,
    QPaintEvent,
)

class RenderArea(QLabel):
    """ Create a "RenderArea".
    This zone is dedicated to the display of several images.

    Main attributes:
        `images` -> represents a stack of QPixmap+information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.images = []

    def push(self, pixmap, opacity=1.0, x=0, y=0):
        """ Push a QPixmap + information into stack.
        """
        self.images.append((
            pixmap,
            opacity, 
            x, 
            y
        ))

    def pop(self):
        """ Pop last element from stack.
        """
        self.images.pop()

    def clear(self):
        """ Clear the stack.
        """
        self.images.clear()

    def paint(self):
        """ Call the `paintEvent()` function.
        """
        self.update()
        self.repaint()
        self.parentWidget().repaint()

    def paintEvent(self, ev: QPaintEvent):
        """ overload of paintEvent Qt function.

        Draw every stacked images with their proprieties
        (i.e.: opacity).

        Images are not 'poped'.
        Stack still has the same size after operation.

        QLabel's size is equals to maximum width & heigth
        found while reading images.
        
        Arguments:
            ev {QPaintEvent} -- A paint event which trigger display.
        """

        painter = QPainter(self)
        images = self.images

        max_w = 0
        max_h = 0

        poped = []

        while images:
            pixmap, opacity, _x, _y = images.pop()
            poped.append((pixmap, opacity, _x, _y))

            painter.setOpacity(opacity)
            painter.drawPixmap(_x, _y, pixmap)

            _w = pixmap.width()
            _h = pixmap.height()

            if _w > max_w:
                max_w = _w
  
            if _h > max_h:
                max_h = _h
        
        painter.end()

        while poped:
            images.append(poped.pop())

        self.setFixedSize(max_w, max_h)