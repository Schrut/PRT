"""
Image module

TASK:
    -(OK) READ
    -(TODO) WRITE
    -(OK) CONVERT to QImage

DEMO opencv-python lib:
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_core/py_basic_ops/py_basic_ops.html#basic-ops

TO READ:
    numpy array:
        https://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html

    tiffile:
        https://github.com/blink1073/tifffile

    qimage2ndarray:
        https://github.com/hmeine/qimage2ndarray
"""

import os
import tifffile as tf
import qimage2ndarray as q2a
import numpy as np

from PyQt5.QtGui import QImage, QPixmap

class Tiff():
    """The Tiff class, represents a TIFF image in memory.
    Attributes:
        name -- image's name
        pname -- image's path
        metadata -- numpy.ndarray, image's bytes
    """

    def __init__(self, pathname):
        """The Tiff class constructor.
        
        Arguments:
            pathname {string} -- the relative or absolute image's path.
        """
        if pathname.endswith(('.tiff', 'tif')):
            if self.load_from(pathname) == False:
                print("Error while reading: image doesn't exists.")
                exit()
            else:
                self.name = os.path.basename(pathname)
                self.pname = pathname
                print("Done.")
        else:
            print("pathname doesn't contains TIFF extension.")
            exit()
    

    def load_from(self, pathname):
        """Load a TIFF image in memory.
        
        Arguments:
            pathname {string} -- the relative or absolute image's path.
        
        Returns:
            boolean -- True if image found.
        """
        print("Loading '"+pathname+"' image.")
        if not os.path.exists(pathname):
            return False
        
        self.metadata = tf.imread(pathname)
        print("Shape ", self.metadata.shape)
        print("Bits ", self.metadata.dtype)
        return True


    def to_QImage(self):
        """Convert the `self.metadata` field (numpy.ndarray) to a QImage
        Thanks to qimage2ndarray library.
        
        Returns:
            QImage -- https://doc.qt.io/qt-5/qimage.html
        """
        return q2a.gray2qimage(self.metadata)
        
    def to_QPixmap(self):
        """Convert QImage to QPixmap.

        Returns:
            QPixmap -- https://doc.qt.io/qt-5/qpixmap.html
        """
        return QPixmap.fromImage(self.to_QImage())