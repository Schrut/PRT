"""
Image module

    smopy:
        https://github.com/rossant/smopy
        https://nbviewer.jupyter.org/github/rossant/smopy/blob/master/examples/example1.ipynb
"""

import os
import numpy as np
import smopy

from libtiff import TIFF

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import (
    QImage, 
    QPixmap, 
    QPainter,
)

from draw import RenderArea

from PyQt5.QtCore import Qt

class Tiff():
    """The Tiff class, represents a TIFF image in memory.

    Attributes:
        name -- image's name
        pname -- image's path
        source -- numpy.ndarray, image's bytes [0;65535] (16-bits)
    """

    name = ""
    pname = ""
    source = None

    def __init__(self, pathname):
        """The Tiff class constructor.

        Arguments:
            pathname {string} -- the relative or absolute image's path.
        """
        if pathname.endswith(('.tiff', 'tif')):
            if self.load_from(pathname) is False:
                print("[FAILED]\nError while reading: image doesn't exists.")
            else:
                self.name = os.path.basename(pathname)
                self.pname = pathname
                print("[OK]")
        else:
            print("[FAILED]\npathname doesn't contains TIFF extension.")

    def load_from(self, pathname):
        """Load a TIFF image in memory.

        Arguments:
            pathname {string} -- the relative or absolute image's path.

        Returns:
            boolean -- True if image found.
        """
        print("Loading image '"+pathname+"' -> ", end="")
        if not os.path.exists(pathname):
            return False
        
        tif = TIFF.open(pathname, 'r')
        self.source = tif.read_image()
        return True

    def size(self):
        return self.source.size

    def shape(self):
        return self.source.shape

    def normalization(self, _min, _max):
        """
        https://en.wikipedia.org/wiki/Normalization_%28image_processing%29
        Linear image normalization.
        """
        smax = self.source.max()
        smin = self.source.min()

        return (self.source - smin) * ((_max - _min)/(smax - smin)) + _min

    def to_8bits(self):
        """Convert the `self.source` field (numpy.ndarray),
        16-bits grayscale image [0;65535] to
        a 8-bits normalized grayscale image [0;255].

        Returns:
            numpy.ndarray (dtype=uint8)
        """
        img = self.normalization(0, 255)
        return img.astype(np.uint8)


    def to_QImage(self):
        """Convert the `self.source` field (numpy.ndarray) to a QImage

        Returns:
            QImage -- https://doc.qt.io/qt-5/qimage.html
        """
        
        img = self.to_8bits()
        _h, _w = img.shape
        return QImage(img, _w, _h, _w, QImage.Format_Grayscale8)

    def to_QPixmap(self):
        """Convert QImage to QPixmap.

        Returns:
            QPixmap -- https://doc.qt.io/qt-5/qpixmap.html
        """
        return QPixmap.fromImage(self.to_QImage())


    def draw_into(self, w):
        """Draw tiff image (QPixmap here) into a widget.

        Arguments:
            w {QWidget} -- the widget in which you want do draw tiff into.
        """
        
        area = RenderArea()
        
        # test --
        area.push_pixm(QPixmap('france.png'), x=50, y=50)
        # test ^^
        
        area.push_pixm(self.to_QPixmap(), 0.8)
        w.setWidget(area)