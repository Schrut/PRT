from os import path, makedirs
from osgeo import gdal
from img import Tiff

"""
# HRV (High Resolution Visible) pictures, as pixels:
hrv_w = 11136
hrv_h = 11136
hrv_psize = 1000.134
hrv_origin = 11136/2 ??

# France coordinates (as pixels) into the HRV image:
top = 10179
bot = 9610
left = 6591
right = 5634

# Pixels width of the source image:
img_h = top - bot
img_w = left - right

# Earth radius as meters:
r_equatorial = 6378169.0
r_polar = 6356583.8

sat_h = 35785831.0
sat_lon = 9.5
""" 

class HRVpicture():
    width: int
    height: int
    psize: float
    origin: float

    def __init__(self, width, height, psize, origin):
        self.width = width
        self.height = height
        self.psize = psize
        self.origin = origin

class Satellite():
    height: float
    lon: float
    lat: float

    def __init__(self, height, lon, lat):
        self.height = height
        self.lon = lon
        self.lat = lat

class PixelZone():
    top: int
    bot: int
    left: int
    right: int

    def __init__(self, top, bot, left, right):
        self.top = top
        self.bot = bot
        self.left = left
        self.right = right

def gdal_translate(tif: Tiff, out_path: str, hrv: HRVpicture, sat: Satellite, zone: PixelZone):
    r_equatorial = 6378169.0
    r_polar = 6356583.8

    ## why??
    xleft = -hrv.psize * (zone.left - hrv.origin)
    ytop = hrv.psize * (zone.top - hrv.origin)
    xright = -hrv.psize * (zone.right - 1 - hrv.origin)
    ybot = hrv.psize * (zone.bot - 1 - hrv.origin)

    _h, _w = tif.shape()

    if not path.exists(out_path):
        makedirs(out_path)

    opt = gdal.TranslateOptions(
        srcWin=[0, 0, _w, _h],
        outputBounds=[xleft, ytop, xright, ybot],
        outputSRS="+proj=geos"
        +" +a="+str(r_equatorial)
        +" +b="+str(r_polar)
        +" +lat_0="+str(sat.lat)
        +" +lon_0="+str(sat.lon)
        +" +h="+str(sat.height)
        +" +x_0=0 +y_0=0 +pm=0",
    )

    gdal.Translate(out_path+tif.name, tif.pname, options=opt)
