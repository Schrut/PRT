import sys
sys.path.insert(0, '..')

from projection import (
    HRVpicture, 
    Satellite, 
    PixelZone, 
    gdal_translate,
    gdal_warp,
)

from img import Tiff

out_path = "../../.cache/gdal/translate/"
tif = Tiff("../../tif/20170407054917_MSG2.tif")

hrv = HRVpicture(11136, 11136, 1000.134, 5565.5)
france = PixelZone(10179, 9610, 6591, 5634)
meteosat9 = Satellite(35785831.0, 9.5, 0.0)

gdal_translate(tif, out_path, hrv, meteosat9, france)

tif = Tiff("../../.cache/gdal/translate/20170407054917_MSG2.tif")
gdal_warp(tif, (958, 570), "../../.cache/gdal/warp/", hrv, meteosat9, france)