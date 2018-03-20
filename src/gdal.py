import os

os.system('gdal_translate -srcwin 0, 0, 958, 570 -a_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0" -a_ullr -1025637.42, 4614118.21, -67509.04, 4044041.83 ../tif/20170407060916_MSG2.tif france_geos.tif')
