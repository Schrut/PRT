"""
PyQt5 QtWidgets
"""
from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QWidget,
    QMenuBar,
    QLabel,
    QAction,
    QFileDialog,
)

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt, QRectF

import numpy as np
import cv2
from img import Tiff

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
		self.setWindowTitle("GDAL TEST")
		self.setFixedSize(600, 400)
		self.show()
		

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
			tiff.draw_In(self.parent.centralWidget())
			self.parent.set_cimg(tiff)

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
		fnames = self.getOpenFileNames(self.parent,
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

		# Create a VideoWirter:
		# output format .MKV
		# encoded using HFYU (Huffman Lossless Codec)
		# 25 frames/sec
		# Size( width, height )
		# False -> not a color video (only grey images here)
		video = cv2.VideoWriter("../video/video.mkv", 
								cv2.VideoWriter_fourcc('H','F','Y','U'), 
								25.0, 
								(_w, _h), 
								False
							)
		
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
	cimg = None # Current image display into MainWindow

	def __init__(self, screen):
			super().__init__()
			self.title = "PRT"
			self.width = 1080
			self.height = 720
			self.left = (screen.size().width() - self.width) / 2
			self.top = (screen.size().height() - self.height) / 2
			self.build()

	def set_cimg(self, tiff):
		self.cimg = tiff

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
			button_process_gdal.setStatusTip("Gdal - Geoloc")
			button_process_gdal.triggered.connect(uiGdal(self).on_click)

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

			## About menu
			menu_about = menu.addMenu("About")
			menu_about.addAction(button_license)