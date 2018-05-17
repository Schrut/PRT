import numpy as np
import cv2
import os

from time import time
from PyQt5.QtWidgets import QProgressBar

def kmeans(paths, nclusters, pbar: QProgressBar):
    # nb sec since 01/01/1970
    timestamp = str(int(time())) 
    spath = "../.cache/kmeans/" + timestamp + "/"

    pbar.setMaximum(len(paths))
    pbar.setEnabled(True)

    if not os.path.exists(spath):
        os.makedirs(spath)

    # Ouput paths
    new_paths = []

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    for file in paths:
        img = cv2.imread(file, -1)
        Z = np.float32(img.ravel())

        ret, label, center = cv2.kmeans(Z, nclusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        center = np.uint16(center) #Convert to 16bits

        res = center[ label.flatten() ]
        res2 = res.reshape((img.shape)) # K-Means images

        sname = spath + os.path.basename(file)
        new_paths.append(sname)

        cv2.imwrite(sname, res2)
        pbar.setValue( pbar.value() + 1)

    pbar.setValue(0)
    pbar.setEnabled(False)

    return new_paths