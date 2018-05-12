import cv2
import numpy as np
import os

from time import time
from PyQt5.QtWidgets import QProgressBar

def histogram_equalization(paths, pbar: QProgressBar):
    timestamp = str(int(time()))
    spath = "../.cache/equalization/" + timestamp + "/"

    pbar.setMaximum(len(paths))
    pbar.setEnabled(True)

    if not os.path.exists(spath):
        os.makedirs(spath)
    
    # Ouput paths
    new_paths = []

    for file in paths:
        image = cv2.imread(file, -1)
        
        # From:
        # https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html
        hist, _ = np.histogram(image.flatten(), 65536, [0, 65536])
        cdf = hist.cumsum()

        # cumulative distribution function
        cdf_m = np.ma.masked_equal(cdf, 0)
        cdf_m = (cdf_m - cdf_m.min())*65535/(cdf_m.max()-cdf_m.min())
        cdf = np.ma.filled(cdf_m, 0).astype('uint16')

        # Equalized image
        im_eq = cdf[image]

        # Save image
        sname = spath + os.path.basename(file)
        new_paths.append(sname)
        cv2.imwrite(sname, im_eq)
        pbar.setValue( pbar.value() + 1 )

    pbar.setValue(0)
    pbar.setEnabled(False)

    return new_paths
