from os import path, makedirs
from osgeo import gdal

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


def gdal_proj_mercator(
    pathname: str, 
    in_w: int, 
    in_h: int, 
    out_w: int, 
    out_h: int, 
    hrv: HRVpicture, 
    sat: Satellite, 
    zone: PixelZone ):
    """Proceed to a Mercator projection, thanks to GDAL.
    
    Arguments:
        pathname {str} -- the pathname of the tiff you want to project.
        in_w {int} -- width of the tiff file.
        in_h {int} -- height of the tiff file.
        out_w {int} -- width after projection.
        out_h {int} -- height after projection.
        hrv {HRVpicture} -- High Resolution Visible picture parameters.
        sat {Satellite} -- Satellite parameters.
        zone {PixelZone} -- A pixel zone from the HRV main picture. 
    """

    # Equatorial & Polar radius, in meters.
    r_equatorial = 6378169.0
    r_polar = 6356583.8

    # Actual corner latitude & longitude.
    xl = -hrv.psize * (zone.left - hrv.origin)
    yt = hrv.psize * (zone.top - hrv.origin)
    xr = -hrv.psize * (zone.right - 1 - hrv.origin)
    yb = hrv.psize * (zone.bot - 1 - hrv.origin)

    ## Check if the tiff pathname exists
    if not path.exists(pathname):
        print("ERROR: filename doesn't exists.")

    # Save tiff's name
    name = path.basename(pathname)
    
    # Save directories
    tr_path = "../.cache/gdal/translate/"
    wr_path = "../.cache/gdal/warp/"

    if not path.exists(tr_path):
        makedirs(tr_path)
    
    if not path.exists(wr_path):
        makedirs(wr_path)

    # Translate options
    opt_translate = gdal.TranslateOptions(
        srcWin=[0, 0, in_w, in_h],
        outputBounds=[xl, yt, xr, yb],
        outputSRS="+proj=geos"
        +" +a="+str(r_equatorial)
        +" +b="+str(r_polar)
        +" +lat_0="+str(sat.lat)
        +" +lon_0="+str(sat.lon)
        +" +h="+str(sat.height)
        +" +x_0=0 +y_0=0 +pm=0",
    )

    # Warp options
    opt_warp = gdal.WarpOptions(
        width=out_w,
        height=out_h,
        srcSRS="+proj=geos"
        +" +a="+str(r_equatorial)
        +" +b="+str(r_polar)
        +" +lat_0="+str(sat.lat)
        +" +lon_0="+str(sat.lon)
        +" +h="+str(sat.height)
        +" +x_0=0 +y_0=0 +pm=0"
        +" +ulx="+str(xl)
        +" +uly="+str(yt)
        +" +lrx="+str(xr)
        +" +lry="+str(yb),
        dstSRS="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
        resampleAlg=gdal.GRIORA_Bilinear,
        multithread=True,
    )

    # Proceed to mercator projection :
    gdal.Translate(tr_path+name, pathname, options=opt_translate)
    gdal.Warp(wr_path+name, tr_path+name, options=opt_warp)

    return wr_path+name
