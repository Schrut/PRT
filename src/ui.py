"""
PyQt5 QtWidgets
"""
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QScrollArea,
	QPushButton,
    QMenuBar,
    QWidget,
    QAction,
    QLabel,
)

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPen,
)

from PyQt5.QtCore import (
    QRectF,
    Qt,
)

"""
https://pypi.python.org/pypi/PythonQwt
"""
"""
from qwt import (
    QwtPlotCurve,
    QwtPlot,
)
"""
import os
import numpy as np
import cv2
from img import Tiff

from histogram import Histogram

class uiLicenseWindow(QMessageBox):
	"""
	The MIT License (MIT)
	https://mit-license.org/
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		self.title = "The MIT License (MIT)"
		#Hardcoded License
		self.license = "<pre><b>Copyright © 2018  <i>~ Thibault HECKEL, Florian GIMENEZ ~</i></b><br><br>\
Permission is hereby granted, free of charge, to any person obtaining a copy<br>\
of this software and associated documentation files (the “Software”), to deal<br>\
in the Software without restriction, including without limitation the rights<br>\
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell<br>\
copies of the Software, and to permit persons to whom the Software is<br>\
furnished to do so, subject to the following conditions:<br><br>\
The above copyright notice and this permission notice shall be included in all<br>\
copies or substantial portions of the Software.<br><br>\
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR<br>\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,<br>\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE<br>\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER<br>\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,<br>\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE<br>\
SOFTWARE.</pre><br>\
Read more at: <a href=\"https://opensource.org/licenses/MIT\">\
https://opensource.org/licenses/MIT</a>"

	def on_click(self):
		self.information(self.parent, self.title, self.license, QMessageBox.Ok)


class uiGdal(QMainWindow):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
		
	
	def on_click(self):
		self.setWindowTitle("GDAL")
		self.setFixedSize(600, 400)

		#Button for a gdal_translate in a geos proj
		self.button_translate_geos = QPushButton('Translate - GEOS',self)
		self.button_translate_geos.move(10, 20)
		self.button_translate_geos.clicked.connect(self.handleButton_TG)
		
		#Button for a gdal_warp in a geos proj
		self.button_warp_geos = QPushButton('Warp - Mercator',self)
		self.button_warp_geos.move(10, 100)
		self.button_warp_geos.clicked.connect(self.handleButton_WG)
		self.show()

	def handleButton_WG(self):
		pathname_in = self.parent.curr_tiff.pname
		if not pathname_in.endswith('translate.tif'):
			print('Not warp to do!')
			print('Translate -> Warp')
			self.close()
			return False
		pathname_out = os.path.basename(pathname_in)
		pathname_out = '../GDAL/Warp/' + pathname_out[:-4] + '_mercator_warp.tif'
		if os.path.exists('../GDAL/Warp/') is False:
			os.makedirs('../GDAL/Warp/')
		os.system('gdalwarp -ts 1916, 1140 -s_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0 +ulx=-1025637.42 +uly=4614118.21 +lrx=-67509.04 +lry=4044041.83" -t_srs  "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs" ' + pathname_in + ' ' + pathname_out)
		tiff = Tiff(pathname_out)
		tiff.draw_into(self.parent.centralWidget())
		self.close()

	def handleButton_TG(self):
		pathname_in = self.parent.curr_tiff.pname
		pathname_out = os.path.basename(pathname_in)
		pathname_out = '../GDAL/Translate/' + pathname_out[:-4] + '_geos_translate.tif'
		if os.path.exists('../GDAL/Translate/') is False:
			os.makedirs('../GDAL/Translate')
		os.system('gdal_translate -srcwin 0, 0, 958, 570 -a_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0" -a_ullr -1025637.42, 4614118.21, -67509.04, 4044041.83 ' + pathname_in + ' ' + pathname_out)
		tiff = Tiff(pathname_out)
		tiff.draw_into(self.parent.centralWidget())
		self.parent.curr_tiff = tiff
		self.close()


class uiOpenFile(QFileDialog):
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent
			
	def on_click(self):
		self.title = "Open a TIFF image"
		fname = self.getOpenFileName(self.parent,
									"Open TIFF image", 
									"..",
									"Image Files (*.tiff *.tif)"
									)[0] # Take only file name

		if fname == "": 
			return
		
		tiff = Tiff(fname)
		tiff.draw_into(self.parent.centralWidget())
		self.parent.curr_tiff = tiff

class uiOpenfFiles(QFileDialog):
	"""
	For the moment, allows user to choose multiples TIFF files.
	Its load pathnames into memory, then create a video 
	(automaticly for the moment, need to add an option)
	from the image sequence choosen.

	This image sequence could then used to "stabilisize" image sequence.

	TODO:
		put video process into an other function/file/class -- nothing to do here.
	"""
	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

	def on_clik(self):
		self.title = "Open multiple TIFF images"
		fnames = self.getOpenFileNames(
			self.parent,
			"Load TIFF images",
			"..",
			"Images Files (*.tiff *tif)"
		)[0]
									  
		frames = len(fnames)

		# If cancel triggered
		if frames == 0:
			return

		# Read first image to check shape
		# Meaning that the whole image sequence choosen
		# must has the same shape (width/height).
		tiff = Tiff(fnames[0])
		_h, _w = tiff.shape()
		
		# Path security check
		videopath = "../video/"
		if os.path.exists(videopath) is False:
			os.makedirs(videopath)

		# Create a VideoWirter:
		# output format .MKV
		# encoded using HFYU (Huffman Lossless Codec)
		# 25 frames/sec
		# Size( width, height )
		# False -> not a color video (only grey images here)
		video = cv2.VideoWriter(
			videopath+"video.mkv", 
			cv2.VideoWriter_fourcc('H','F','Y','U'), 
			25.0, 
			(_w, _h), 
			False
		)
		
		# If the VideoWriter creation failed, exit.
		# e.g.:
		# HFYU codec is not present at runtime on the machine.
		if video.isOpened() is False:
			print("Video [FAILED]")
			return

		# Remember that we read the first sequence image.
		# During the process, 16-bits greyscale images
		# are converted to 8-bits.
		video.write(tiff.to_8bits())
		fnames.pop(0)
		
		# Now read all the others.
		for fname in fnames:
			tiff = Tiff(fname)
			video.write(tiff.to_8bits())

		# "close" VideoWriter.
		video.release()
		print("Video [DONE]")

"""
User Interface Main Window
"""
class uiMainWindow(QMainWindow):
	curr_tiff = None # Current Tiff
	prev_tiff = None # Previous Tiff into list
	next_tiff = None # Next Tiff into list

	def __init__(self, screen):
		super().__init__()
		self.title = "PRT"
		self.width = 1080
		self.height = 720
		self.left = (screen.size().width() - self.width) / 2
		self.top = (screen.size().height() - self.height) / 2
		self.build()

	def draw_histogram(self):
		if self.curr_tiff is not None:
			Histogram(self, self.curr_tiff.source)

	def build(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)

		scroll_area = QScrollArea()
		self.setCentralWidget(scroll_area)

		# Buttons
		## Exit button
		button_exit = QAction("Exit", self)
		button_exit.setShortcut("Ctrl+Q")
		button_exit.setStatusTip("Exit application")
		button_exit.triggered.connect(self.close)

		## Open-File button
		button_open = QAction("Open TIFF image", self)
		button_open.setShortcut("Ctrl+O")
		button_open.setStatusTip("Open an image")
		button_open.triggered.connect(uiOpenFile(self).on_click)

		## Open-FileS button
		button_open_mult = QAction("Load TIFF images", self)
		button_open_mult.setShortcut("Ctrl+L")
		button_open_mult.setStatusTip("Open multiple TIFF")
		button_open_mult.triggered.connect(uiOpenfFiles(self).on_clik)

		## Show License button
		button_license = QAction("License", self)
		button_license.setStatusTip("Application's license")
		button_license.triggered.connect(uiLicenseWindow(self).on_click)

		## Process Gdal button
		button_process_gdal = QAction("Gdal", self)
		button_process_gdal.setShortcut("Ctrl+G")
		button_process_gdal.setStatusTip("Gdal - Geoloc")
		button_process_gdal.triggered.connect(uiGdal(self).on_click)

		
		button_process_histo = QAction("Histogram", self)
		button_process_histo.setShortcut("Ctrl+H")
		button_process_histo.triggered.connect(self.draw_histogram)
		
		# Menus
		# Main menu
		menu = self.menuBar()

		## File menu
		menu_file = menu.addMenu("File")
		menu_file.addAction(button_open)
		menu_file.addAction(button_open_mult)
		menu_file.addSeparator()
		menu_file.addAction(button_exit)

		## Process menu
		menu_process = menu.addMenu("Process")
		menu_process.addAction(button_process_gdal)
		menu_process.addAction(button_process_histo)

		## About menu
		menu_about = menu.addMenu("About")
		menu_about.addAction(button_license)
