"""
Image module

TASK:

    -(OK) READ
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

    tiffile:
        https://github.com/blink1073/tifffile
        https://www.lfd.uci.edu/%7Egohlke/code/tifffile.py.html

    qimage2ndarray:
        https://github.com/hmeine/qimage2ndarray

    smopy:
        https://github.com/rossant/smopy
        https://nbviewer.jupyter.org/github/rossant/smopy/blob/master/examples/example1.ipynb
"""

import os
import gdal
import smopy
from osgeo import gdal
import numpy as np
import qimage2ndarray as q2a

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
        
        self.metadata = gdal.Open(pathname).ReadAsArray() # Convert TIFF to numpy.ndarray

        # Les metadatas du TIFF, celles qui nous intéresses ici sont les fameuses GEOTIFF
        # print( gdal.Info(pathname) )

        return True


    def to_QImage(self):
        """Convert the `self.metadata` field (numpy.ndarray) to a QImage
        Thanks to qimage2ndarray library.
        Normalize image (dynamic range expansion)
        
        Returns:
            QImage -- https://doc.qt.io/qt-5/qimage.html
        """
        _min = self.metadata.min()
        _max = self.metadata.max()
        return q2a.gray2qimage(self.metadata, (_min, _max))

        #### smopy test lib ####
        #_map = smopy.Map((48., -1., 52., 3.), z=5)
        #_map.save_png('test.png')
        #return QImage('test.png')
        #### works great ####
        
    def to_QPixmap(self):
        """Convert QImage to QPixmap.

        Returns:
            QPixmap -- https://doc.qt.io/qt-5/qpixmap.html
        """
        return QPixmap.fromImage(self.to_QImage())
