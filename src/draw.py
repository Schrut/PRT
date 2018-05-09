from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter

class RenderArea(QLabel):
    """ Create a "RenderArea".
    This zone is dedicated to the display of several images.

    Main attributes:
        `images` -> represents a stack of QImage+information.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.images = []
        self.pos = (0, 0)
        self.setMouseTracking(True)

    def push(self, image, opacity=1.0, x=0, y=0):
        """ Push a QImage + information into stack.
        """
        self.images.append((
            image,
            opacity, 
            x, 
            y
        ))

    def pop(self):
        """ Pop last element from stack.
        """
        return self.images.pop()

    def clear(self):
        """ Clear the stack.
        """
        self.images.clear()

    def paintEvent(self, event):
        """ overload of paintEvent Qt function.

        Draw every stacked images with their proprieties
        (i.e.: opacity).
        
        Stack still has the same size after operation.

        QLabel's size is equals to maximum width & height
        found while reading images.
        
        Arguments:
            ev {QPaintEvent} -- A paint event which trigger display.
        """

        if not self.images:
            return

        painter = QPainter(self)

        max_h: int = 0
        max_w: int = 0

        for image in self.images:

            qimage, opacity, _x, _y = image

            painter.setOpacity(opacity)
            painter.drawImage(_x, _y, qimage)

            _h = qimage.height()
            _w = qimage.width()

            if _h > max_h:
                max_h = _h
            
            if _w > max_w:
                max_w = _w

        self.setFixedSize(max_w, max_h)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        self.pos = ( x, y )
        self.parent.img_posX.setText( str(x) )
        self.parent.img_posY.setText( str(y) )
