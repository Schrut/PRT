"""
PyQt5 QtWidgets

User Interface classes.
"""
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMenuBar,
    QWidget,
    QAction,
    QWidget,
    QSlider,
    QLabel,
    QMenu,
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

import os
import numpy as np
import cv2

from draw import RenderArea
from img import Tiff, TiffSequence

from histogram import Histogram

import smopy

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
		
	"""
	Here the GDAL happen.
	In two steps : 
		-Translate which will geolocate the image
		-Warp will scaled the image
	"""

	"""
	GDAL doit charger toute la séquence et la transformer pour pouvoir ouvrir une séquence géoloc et OK pour l'affichage.
	"""
	def on_click(self):
		"""
		#
		# TODO:
		#	Total rework with the tiff sequence needed

		#Pick the current image pathname
		pathname_in = self.parent.curr_tiff.pname
		
		#Take only the basename/file name
		pathname_out = os.path.basename(pathname_in)

		#Define the pathname for the output
		pathname_out = '../GDAL/Translate/' + pathname_out[:-4] + '_geos_translate.tif'

		#Create a GDAL folder if necessary
		if os.path.exists('../GDAL/Translate/') is False:
			os.makedirs('../GDAL/Translate')

		#The actual GDAL transformation
		os.system('gdal_translate -srcwin 0, 0, 958, 570 -a_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0" -a_ullr -1025637.42, 4614118.21, -67509.04, 4044041.83 ' + pathname_in + ' ' + pathname_out)
		
		#Drawing the Image
		tiff = Tiff(pathname_out)
		tiff.draw_into(self.parent.centralWidget())
		self.parent.curr_tiff = tiff


		#Same thing here, but this time we warp the image
		pathname_in = self.parent.curr_tiff.pname
		pathname_out = os.path.basename(pathname_in)
		pathname_out = '../GDAL/Warp/' + pathname_out[:-4] + '_mercator_warp.tif'
		if os.path.exists('../GDAL/Warp/') is False:
			os.makedirs('../GDAL/Warp/')
		os.system('gdalwarp -ts 1916, 1140 -s_srs "+proj=geos +a=6378169.0 +b=6356583.8 +lon_0=9.5 +h=35785831.0 +x_0=0 +y_0=0 +pm=0 +ulx=-1025637.42 +uly=4614118.21 +lrx=-67509.04 +lry=4044041.83" -t_srs  "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs" ' + pathname_in + ' ' + pathname_out)
		tiff = Tiff(pathname_out)
		tiff.draw_into(self.parent.centralWidget())
		self.parent.curr_tiff = tiff
		"""


"""
User Interface Main Window
"""
class uiMainWindow(QMainWindow):
	draw_area: RenderArea = None
	tifs: TiffSequence = None # Tiff images sequences
	img_slider_old: int = 0

	def __init__(self, screen):
		super().__init__()
		self.title = "PRT"
		self.width = 1080
		self.height = 720
		self.left = (screen.size().width() - self.width) / 2
		self.top = (screen.size().height() - self.height) / 2
		self.build()

	##### SIGNALS #####
	def img_slider_moved(self, value):
		"""When slider's value has changed, do something:

			if previous value + step >= current value
				move right
			else
			if previous value - step <= current value
				move left

			If user move the slider to fast, it's possible that
			the distance between the old and the current value is
			superior to the `step` value. 
			In this case, we need to call the `active()` function.
		
		Arguments:
			value {integer} -- current integer value of the slider.
		"""

		moved = False
		step = self.img_slider.singleStep()
		old = self.img_slider_old # previous value

		l_new = old-step # new possible left value
		r_new = old+step # new possible right value

		if value <= l_new:
			moved = True
			if value is l_new:
				self.tifs.shift_left()
			else:
				self.tifs.active(int(value/step))
		
		elif value >= r_new:
			moved = True
			if value is r_new:
				self.tifs.shift_right()
			else:
				self.tifs.active(int(value/step))

		if moved:
			self.img_slider_old = value
			_, tif = self.tifs.current()

			self.draw_area.clear()
			self.draw_area.push(tif.to_QPixmap())
			self.draw_area.paint()
			self.img_area.setWidget(self.draw_area)

	def draw_histogram(self):
		if self.tifs:
			_, tif = self.tifs.current()
			Histogram(self, tif.source, tif.name)

	def load_tiffs(self):
		"""Load multiples tiffs into memory
		"""
		fnames = QFileDialog.getOpenFileNames(
			self, 
			"Load a Tiff sequence", 
			"..",
			"Images Files (*.tiff *.tif)"
		)[0]

		if not fnames:
			return

		# Save the new sequence
		self.tifs = TiffSequence(fnames)

		# update the slider
		size = self.tifs.size()
		width = self.img_slider.width()

		step = int(width/size)
		if step is 0:
			step = 1
		
		self.img_slider.setEnabled(True)
		self.img_slider.setValue(0)
		self.img_slider.setMaximum( (size-1)*step )
		self.img_slider.setSingleStep(step)
		self.img_slider.setTickInterval(step)
		self.img_slider.setTickPosition(QSlider.TicksBelow)

		# Reset the "old position" of the current slider.
		self.img_slider_old = 0
		
		_, tif = self.tifs.current()

		print(self.img_area.widget())

		self.draw_area.clear()
		self.draw_area.push(tif.to_QPixmap())
		self.draw_area.paint()

	###### Interface ######
	def build_left_vbox(self):
		# Where we are going to draw images
		s_area = QScrollArea()

		# The main slider
		slider = QSlider(Qt.Horizontal)
		slider.setEnabled(False) # Not usable
		slider.setFocusPolicy(Qt.StrongFocus) # Mouse & Keyboard can move it
		slider.setTickPosition(QSlider.NoTicks) # No ticks draw
		slider.valueChanged.connect(self.img_slider_moved) # What do you do when slider is moved ?
		
		# The Left Vertical Box Layout
		vbox = QVBoxLayout()
		vbox.addWidget(s_area)
		vbox.addWidget(slider)

		# Usefull attributes
		self.img_area = s_area
		self.img_slider = slider

		return vbox

	def build_right_vbox(self):
		button = QPushButton("Try")
		#button.triggered.connect()

		vbox = QVBoxLayout()
		vbox.addWidget(button)
		return vbox

	def build_grid(self):
		grid = QGridLayout()
		grid.addLayout(self.build_left_vbox(), 0, 0)
		grid.addLayout(self.build_right_vbox(), 0, 1)
		return grid

	def build_main_widget(self):
		widget = QWidget()
		widget.setLayout(self.build_grid())
		return widget

	####### MENU #######
	def action_close(self):
		action = QAction("Close", self)
		action.setShortcut("Ctrl+Q")
		action.triggered.connect(self.close)
		return action

	def action_load_tiffs(self):
		action = QAction("Open Tiffs", self)
		action.setShortcut("Ctrl+O")
		action.triggered.connect(self.load_tiffs)
		return action

	def action_show_license(self):
		action = QAction("License", self)
		action.setShortcut("Ctrl+L")
		action.triggered.connect(uiLicenseWindow(self).on_click)
		return action

	def action_draw_histogram(self):
		action = QAction("Histogram", self)
		action.setShortcut("Ctrl+H")
		action.triggered.connect(self.draw_histogram)
		return action

	def menu_file(self):
		menu = QMenu("File", self.menuBar())
		menu.addAction(self.action_load_tiffs())
		menu.addSeparator()
		menu.addAction(self.action_close())
		return menu

	def menu_process(self):
		menu = QMenu("Process", self.menuBar())
		menu.addAction(self.action_draw_histogram())
		return menu
	
	def menu_about(self):
		menu = QMenu("About", self.menuBar())
		menu.addAction(self.action_show_license())
		return menu

	def build_menu(self):
		menu = self.menuBar()
		menu.addMenu(self.menu_file())
		menu.addMenu(self.menu_process())
		menu.addMenu(self.menu_about())

	###### BUILD ALL ######
	def build(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setMinimumSize(self.width, self.height)
		self.build_menu()
		self.setCentralWidget(self.build_main_widget())

		self.draw_area = RenderArea(self.img_area)
		self.img_area.setWidget(self.draw_area)

		###### need a rework
		## Process Gdal button
		#button_process_gdal = QAction("Gdal", self)
		#button_process_gdal.setShortcut("Ctrl+G")
		#button_process_gdal.setStatusTip("Gdal - Geoloc")
		#button_process_gdal.triggered.connect(uiGdal(self).on_click)
