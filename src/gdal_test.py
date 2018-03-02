#gdal_translate - srcwin 0, 0, 958, 570 - a_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0" - a_ullr - 1025637.42, 4614118.21, -67509.04, 4044041.83 20170407054917_MSG2.tif france_geos.tif
from osgeo import gdal
import numpy


def array_to_raster(array):
    """Array > Raster
    Save a raster from a C order array.

    :param array: ndarray
    """
    ds = gdal.Open('../tif/france_mercator.tif')
    ts = gdal.Open('../tif/20170407054917_MSG2.tif', gdal.GA_Update)

    geotransform = ds.GetGeoTransform()
    if geotransform:
        print("Origin = ({}, {})".format(geotransform[0], geotransform[3]))
        print("Pixel Size = ({}, {})".format(geotransform[1], geotransform[5]))



    ts = ts.SetGeoTransform(geotransform)
    ts.SetProjection('+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0')
    ts.GetRasterBand(1).WriteArray(array)









"""
Stabilisation : http://answers.opencv.org/question/6843/realtime-video-stabilization/
"""
