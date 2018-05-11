import cv2
from skimage.feature import local_binary_pattern
import matplotlib.pyplot as plt
import numpy as np
import os

path = "../../tif/"
fichiers = os.listdir(path)

for fichier in fichiers:
    image = cv2.imread(path+fichier, -1)

    #plt.imshow(image, cmap=plt.get_cmap('gray'))
    #plt.show()
    
    
    # Paramètres du calcul de LBP 
    radius = 1
    n_points = 8 * radius
    L = local_binary_pattern(image, n_points, radius, method='default')

    cv2.imwrite(fichier, L.astype("uint16"))
