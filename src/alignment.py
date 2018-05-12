import cv2
import numpy as np
import os

from time import time
from PyQt5.QtWidgets import QProgressBar

from img import Tiff

# Image Registration using 
# Enhanced Correlation Coefficient (ECC) Maximization
def images_alignement(one, two, outpath):
    _h, _w = one.shape

    # Define 2x3 and initialize the matrix to identity
    warp_matrix = np.eye(2, 3, dtype=np.float32)

    # Specify the number of iterations
    number_of_iterations = 5000
    
    # Specify the threshold of the increment
    # in the correlation coefficient between two iterations
    termination_eps = 1e-10
    
    # Define termination criteria
    criteria = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        number_of_iterations,
        termination_eps
    )

    # Run the ECC algorithm. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (
        one, two,
        warp_matrix, 
        cv2.MOTION_TRANSLATION, 
        criteria
    )

    # Use warpAffine for Translation, Euclidean and Affine
    three = cv2.warpAffine(
        two, 
        warp_matrix, (_w, _h), 
        flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
    )

    # Save image
    cv2.imwrite(outpath, three.astype('uint16'))
    return outpath


def alignement(paths, pbar: QProgressBar):
    timestamp = str(int(time()))
    spath = "../.cache/alignment/" + timestamp + "/"

    pbar.setMaximum(len(paths))
    pbar.setEnabled(True)

    if not os.path.exists(spath):
        os.makedirs(spath)

    new_paths = []

    # Algorithm need to work with 8bits images
    one = Tiff(paths[0]).to_8bits()
    sname = spath + os.path.basename(paths[0])
    new_paths.append(sname)
    cv2.imwrite(sname, one.astype('uint16'))

    for i in range(1, len(paths)):
        two = Tiff(paths[i]).to_8bits()

        sname = spath + os.path.basename(paths[i])

        new_paths.append(
            images_alignement(one, two, sname)
        )

        one = two

        pbar.setValue( pbar.value() + 1 )
    
    pbar.setValue(0)
    pbar.setEnabled(False)

    return new_paths