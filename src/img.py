"""
Image module
"""

from os import path, makedirs
from time import time
from osgeo import gdal
from numpy import uint8, histogram
from cv2 import VideoWriter, VideoWriter_fourcc
from tifffile import imread
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage, QPixmap, QColor
import qimage2ndarray as q2a

from draw import RenderArea

class TiffSequence():
    """A list of TIFF images.
    Minimum 2 & maximum 3 images are loaded into memory.

    Each `shit_left()` & `shift_right()` function
    load only one new image into memory.
    """
    paths = []
    img_number = 0

    img_curr = ()
    img_prev = ()
    img_next = ()

    def __init__(self, paths):
        self.paths = paths
        self.img_number = len(paths)
        self.active(0)

    def size(self):
        return self.img_number

    def current(self):
        return self.img_curr

    def previous(self):
        return self.img_prev
    
    def nextone(self):
        return self.img_next

    def clear(self):
        self.img_next = None
        self.img_prev = None
        self.img_next = None
        self.img_number = 0
        self.paths = []

    def set_previous(self, index):
        """Set previous neighbour

        corner case:
            current image == previous image

        Arguments:
            index {integer} -- Index between [0, self.img_number[
        """

        if index is 0:
            self.img_prev = self.img_curr
        else:
            self.img_prev = (index-1, Tiff(self.paths[index-1]))


    def set_nextone(self, index):
        """Set next neighbour

        corner case:
            current image == next image

        Arguments:
            index {integer} -- Index between [0, self.img_number[
        """
        if index is self.img_number-1:
            self.img_next = self.img_curr
        else:
            self.img_next = (index+1, Tiff(self.paths[index+1]))


    def active(self, index):
        """`active` a given image thanks to its index.
        Will change the current image, and its neighbours into memory.

        Arguments:
            index {integer} -- Index between [0, self.img_number[
        """
        # No paths given
        if not self.paths:
            return
       
        # Index given is out of range.
        elif index < 0 or self.img_number <= index:
            return

        # Read the current (active) image
        self.img_curr = (index, Tiff(self.paths[index]))
        self.set_previous(index)
        self.set_nextone(index)


    def shift_left(self):
        """Shift the memory to the left.
        -> previous image become the new current image.
        """

        if self.img_curr[0] is 0:
            return

        self.img_next = self.img_curr
        self.img_curr = self.img_prev
        self.set_previous(self.img_curr[0])


    def shift_right(self):
        """Shift the memory to the right.
        -> next image become the new current image.
        """
        
        if self.img_curr[0] is self.img_number-1:
            return
        
        self.img_prev = self.img_curr
        self.img_curr = self.img_next
        self.set_nextone(self.img_curr[0])

    def as_video(self, pathname: str):
        if self.img_number is 0:
            print("Warning: no images into this TiffSequence.")
            print("Warning: cannot build a video from this image sequence.")
            return

        # Path security check
        if not path.exists(pathname):
            makedirs(pathname)

        # Save the current active image from the sequence.
        old = self.current()[0]

        # Now reset to 0
        self.active(0)

        # The whole video will have the same shape than
        # the first sequence image.
        idx, tif = self.current()
        _h, _w = tif.shape()

        # video name, based on the current timestamp.
        # output format is '.MKV'
        vname = pathname+str( time() )+".mkv"
        
        # Create a VideoWirter:
        # encoded using HFYU (Huffman Lossless Codec)
        # 25 frames/sec
        # Size( width, height )
        # False -> no color images.
        video = VideoWriter(
            vname, 
            VideoWriter_fourcc('H','F','Y','U'), 
            25.0, 
            (_w, _h), 
            False
        )

        # If the VideoWriter creation failed, exit.
        # e.g.:
        # HFYU codec is not present at runtime on the machine.
        if video.isOpened() is False:
            print("Video failed to build.")
            return
        
        # Remember that we alreay read the first sequence image.
        # During the process, 16-bits greyscale images
        # are converted to 8-bits.
        video.write( tif.to_8bits() )
        
        # Read the complete sequence.
        while idx+1 is not self.img_number:
            self.shift_right()
            idx, tif = self.current()
            video.write( tif.to_8bits() )

        # Close the VideoWriter
        video.release()

        # Put back the sequence in the way
        # it was before building video.
        self.active(old)


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

    def __init__(self, pathname: str):
        """The Tiff class constructor.

        Arguments:
            pathname {string} -- the relative or absolute image's path.
        """
        if pathname.endswith(('.tiff', 'tif')):
            if self.load_from(pathname) is False:
                print("[FAILED]\nError while reading: image doesn't exists.")
            else:
                self.name = path.basename(pathname)
                self.pname = pathname
        else:
            print("[FAILED]\npathname doesn't contains TIFF extension.")

    def load_from(self, pathname):
        """Load a TIFF image in memory.

        Arguments:
            pathname {string} -- the relative or absolute image's path.

        Returns:
            boolean -- True if image found.
        """
        if not path.exists(pathname):
            return False
        
        self.source = imread(pathname)
        return True

    def size(self):
        return self.source.size

    def shape(self):
        return self.source.shape

    def dtype(self):
        return self.source.dtype.name
    
    def histogram(self):
        """Calcul histogram of the tiff source.
        
        Returns:
            histogram, bin_edges
        """
        return histogram(self.source.ravel(), bins='auto')

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
        return img.astype(uint8)


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
