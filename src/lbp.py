import cv2
from skimage.feature import local_binary_pattern
import numpy as np
import os
from time import time

from PyQt5.QtWidgets import QProgressBar

def lbp(paths, radius, pbar: QProgressBar):
    # nb sec since 01/01/1970
    timestamp = str(int(time())) 
    spath = "../.cache/lbp/" + timestamp + "/"

    pbar.setMaximum(len(paths))
    pbar.setEnabled(True)

    if not os.path.exists(spath):
        os.makedirs(spath)

    # Ouput paths
    new_paths = []

    # LBP calcul parameters
    n_points = 8 * radius

    for file in paths:
        image = cv2.imread(file, -1)
        
        result = local_binary_pattern(image, n_points, radius, method='default')

        sname = spath + os.path.basename(file)
        new_paths.append(sname)

        cv2.imwrite(sname, result.astype("uint16"))
        pbar.setValue( pbar.value() + 1)

    pbar.setValue(0)
    pbar.setEnabled(False)

    return new_paths
