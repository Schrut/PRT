import cv2
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt
import numpy as np
import os
from time import time

from PyQt5.QtWidgets import QProgressBar

def lbp(paths, pbar: QProgressBar):
    spath = "../.cache/lbp/" + str(int(time())) + "/"

    pbar.setMaximum(len(paths))
    pbar.setEnabled(True)

    if not os.path.exists(spath):
        os.makedirs(spath)

    new_paths = []

    for file in paths:
        image = cv2.imread(file, -1)
    
        # Paramètres du calcul de LBP 
        radius = 1
        n_points = 8 * radius
        result = local_binary_pattern(image, n_points, radius, method='default')

        sname = spath + os.path.basename(file)
        new_paths.append(sname)

        cv2.imwrite(sname, result.astype("uint16"))
        pbar.setValue( pbar.value() + 1)

    pbar.setValue(0)
    pbar.setEnabled(False)

    return new_paths
