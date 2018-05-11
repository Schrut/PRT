from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QImage
from PyQt5.Qt import Qt, QRect

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
        self.opacities = []
        self.xx = []
        self.yy = []

        self.setMouseTracking(True)
        self.rect_color = Qt.yellow
        self.draw_rect = False
        self.l_pos = None #Left Position
        self.r_pos = None #Right Position
        self.zlevel = 4 # Zoom level
        self.zstep = 0.25 # Zoom step
        self.step = 0

    def zoom(self):
        return self.zlevel * self.zstep

    def push(self, image, opacity=1.0, x=0, y=0):
        """ Push a QImage + information into stack.
        """
        self.images.append(image)
        self.opacities.append(opacity)
        self.xx.append(x)
        self.yy.append(y)

    def pop(self):
        """ Pop last element from stack.
        """
        return (
            self.images.pop(), 
            self.opacities.pop(), 
            self.xx.pop(), 
            self.yy.pop()
        )

    def clear(self):
        """ Clear the stack.
        """
        self.images.clear()
        self.opacities.clear()
        self.xx.clear()
        self.yy.clear()

        self.zlevel = 4
        self.step = 0


    def save(self, filename: str, do_crop: bool=False):
        """Save a RenderIrea as one image on disk.
        
        Arguments:
            filename {str} -- The filename of the new image.
        """
        if not self.images:
            return

        # new label size
        dst_w = 0
        dst_h = 0

        # Zoom
        zoom = self.zoom()

        # Current number of images into the stack.
        nbimg = len(self.images)

        # Find the current size of the output image.
        images = []
        for i in range(0, nbimg):
            image = self.images[i]

            _w = image.width() * zoom
            _h = image.height() * zoom

            if _w > dst_w:
                dst_w = _w
            
            if _h > dst_h: 
                dst_h = _h

            # Scale now
            images.append(
                image.scaled(
                _w, _h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))

        # Output image
        # ARGB since we can have all types of images (colors/grayscale/alpha channel)
        dst = QImage(dst_w, dst_h, QImage.Format_ARGB32)
        dst.fill(0) # black pixels everywhere

        # Init QPainter.
        painter = QPainter()
        painter.begin(dst) # Begin to draw inside the `dst` Image

        # Draw every stacked images.
        # From the bottom of the stack to the top.
        for i in range(0, nbimg):
            # Opacity
            painter.setOpacity(self.opacities[i])
            painter.drawImage(
                self.xx[i] * zoom,
                self.yy[i] * zoom,
                images[i]
            )

        painter.end()

        # Crop or not to crop?
        if do_crop and self.draw_rect:
            rect = QRect(self.l_pos, self.r_pos)
            dst = dst.copy(rect)

        # Save image, max quality
        dst.save(filename, None, 100)
        

    def paintEvent(self, event):
        """ overload of paintEvent Qt function.

        Draw every stacked images with their proprieties
        (i.e.: opacity).
        
        Stack still has the same size after operation.

        Image are scaled during the process.

        QLabel's size is equals to maximum width & height
        found while reading images.
        
        Arguments:
            ev {QPaintEvent} -- A paint event which trigger display.
        """
        if not self.images:
            return

        # new label size
        area_w = 0
        area_h = 0

        # Zoom
        zoom = self.zoom()

        # Init QPainter.
        painter = QPainter(self)

        # Draw every stacked images.
        # From the bottom of the stack to the top.
        for i in range(0, len(self.images)):
            # Opacity
            painter.setOpacity(self.opacities[i])
            
            # Scale and Draw
            image = self.images[i]
            
            _w = image.width() * zoom
            _h = image.height() * zoom

            if _w > area_w:
                area_w = _w
            
            if _h > area_h: 
                area_h = _h

            painter.drawImage(
                self.xx[i] * zoom,
                self.yy[i] * zoom, 
                image.scaled(
                    _w, _h,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        if self.draw_rect is True:
            painter.setPen(QPen(self.rect_color))
            painter.drawRect(QRect(self.l_pos, self.r_pos))

        self.setFixedSize(area_w, area_h)

    def mouseMoveEvent(self, event):
        """When mouse is moved.
        -> update x & y coordinates
        -> left button pressed: update right coordinate, draw rectangle.
        
        Arguments:
            event {QMouseEvent} -- 
        """
        if not self.parent is None:
            self.parent.img_posX.setText( str(event.x()) )
            self.parent.img_posY.setText( str(event.y()) )

        if event.buttons() == Qt.LeftButton:
            self.r_pos = event.pos()
            self.update() # redraw.

    def mousePressEvent(self, event):
        """When mouse is pressed:
        -> Left button, update left corner of the rectangle.
        -> Right button, disable the drawing of the rectangle.
        
        Arguments:
            event {QMouseEvent} --
        """

        if event.buttons() == Qt.LeftButton:
            self.l_pos = event.pos()
            self.draw_rect = True

        elif event.buttons() == Qt.RightButton:
            self.draw_rect = False
            self.update()

    def mouseReleaseEvent(self, event):
        """When mouse is released:
        -> Left button, update right corner of the rectangle.
        
        Arguments:
            event {QMouseEvent} --
        """

        if event.buttons() == Qt.LeftButton:
            self.r_pos = event.pos()
            self.update()

    def wheelEvent(self, event):
        """When the mouse wheel is in movement.

        Update the scaling of our images.
        
        Arguments:
            event {QWheelEvent} --
        """
        # 120 / 4 -> 30, 4*30 degree of mouse scroll to count a step.
        delta = event.angleDelta().y() / 4.0

        # Check if the step is a multiple of 120.
        self.step += delta
        if (self.step % 120) != 0 :
            return

        # Scroll forwards
        if delta < 0:
            if self.zlevel is not 8:
                self.zlevel += 1

                # Scale ROI
                if self.draw_rect:
                    step = self.zlevel/(self.zlevel-1)
                    self.r_pos *= step
                    self.l_pos *= step
        
        # Scroll backwards
        else:
            if self.zlevel is not 1:
                self.zlevel -= 1

                # Scale ROI
                if self.draw_rect:
                    step = self.zlevel/(self.zlevel+1)
                    self.r_pos *= step
                    self.l_pos *= step

        # Update the scale info.
        if not self.parent is None:
            self.parent.update_img_info()
        self.update()
