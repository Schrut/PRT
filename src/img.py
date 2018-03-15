"""
Image module

TASK:

    -(OK) READ
    -(OK) CONVERT to 8bits
    -(OK) CONVERT to QImage
    -(OK) CONVERT to QPixmap

    -(TODO) WRITE
    -(TODO) Pouvoir accéder à une liste d'image dans un dossier (Boîte de dialogue modale pour l'utilisateur).
    -(TODO) Proposer différentes transformations grâce à GDAL, Mercator ...
    -(TODO) Permettre la visualisation des images par dessus une map OSM (gérer la transparence/superposition).
    -(TODO) Implémenter le zoom/dézoom (+tout ce que cela implique avec la transparence/superposition).
    -(TODO) [...]

DEMO opencv-python lib:
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_core/py_basic_ops/py_basic_ops.html#basic-ops

TO READ:
    numpy array:
        https://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html

    smopy:
        https://github.com/rossant/smopy
        https://nbviewer.jupyter.org/github/rossant/smopy/blob/master/examples/example1.ipynb
"""

import os
#import smopy
from osgeo import gdal
import numpy as np
import cv2

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QImage, QPixmap


#### smopy test lib ####
#_map = smopy.Map((48., -1., 52., 3.), z=5)
#_map.save_png('test.png')
#return QImage('test.png')
#### works great ####



class Tiff():
    """The Tiff class, represents a TIFF image in memory.

    Attributes:
        name -- image's name
        pname -- image's path
        source -- numpy.ndarray, image's bytes [0;65536] (16-bits)
    """

    name = ""
    pname = ""
    metadata = None
    img = None

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

        # Read TIFF as numpy.ndarray
        self.source = gdal.Open(pathname).ReadAsArray()


        # Les metadatas du TIFF, celles qui nous intéresses ici sont les fameuses GEOTIFF
        # print( gdal.Info(pathname) )

        return True


    def to_8bits(self):
        """Convert the `self.source` field (numpy.ndarray),
        16-bits grayscale image [0;65536] to
        a 8-bits normalized grayscale image [0;255].

        Returns:
            numpy.ndarray (dtype=uint8)
        """

        # First, clone source
        img = np.copy(self.source)

        # Then, normalize to [0;255]
        cv2.normalize(self.source, img, 0, 255, cv2.NORM_MINMAX)

        # Now, convert dtype without issues and return
        return img.astype(np.uint8)


    def to_QImage(self):
        """Convert the `self.metadata` field (numpy.ndarray) to a QImage

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


    def draw_In(self, wp):
        """Draw tiff image (QPixmap here) into a widget.

        Arguments:
            wp {QWidget} -- the widget in which you want do draw tiff into.

        """
        img_viewer = QLabel()
        img_viewer.setPixmap(self.to_QPixmap())
        wp.setWidget(img_viewer)
