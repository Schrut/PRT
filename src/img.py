"""
Image module

TODO:
    -(OK) READ
    -() WRITE
    -() CONVERT to QImage

TUTO for the openCV-python Lib:
    https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_core/py_basic_ops/py_basic_ops.html#basic-ops
"""

import os
import cv2
from PyQt5.QtGui import QImage, QPixmap

class Image():

    def __init__(self, pathname):
        # Debug
        print("OpenCV version: "+cv2.__version__)

        if pathname.endswith(('.tiff', 'tif')):
            if self.load_from(pathname) == False:
                print("Error while reading: image doesn't exists.")
            else:
                print("Done.")
        else:
            print("pathname doesn't contains TIFF extension.")
    

    def load_from(self, pathname):
        print("Loading '"+pathname+"' image.")
        if not os.path.exists(pathname):
            return False
        
        self.metadata = cv2.imread(pathname, cv2.IMREAD_ANYDEPTH)
        print("NB-Bits DEPTH:", self.metadata.dtype)
        print("Shape:", self.metadata.shape)
        return True

    def cvt_to_QImage(self):
        #cv_img = (self.metadata).astype('uint8') # Convert 16-bit to 8-bit
        #cv_img = cv2.merge((self.metadata, self.metadata, self.metadata))
        #cv_img = cv2.cvtColor(self.metadata, cv2.)
        cv_img = cv2.cvtColor(self.metadata, cv2.COLOR_GRAY2BGR)
        # Debug
        cv2.imwrite("./cv_img.png", cv_img)

        # Debug
        print(cv_img.shape)
        print(cv_img.dtype)

        q_img = QImage(cv_img, self.metadata.shape[1], self.metadata.shape[0], QImage.Format_RGB16)
        return q_img
        
    def cvt_to_QPixmap(self):
        return QPixmap.fromImage(self.cvt_to_QImage())