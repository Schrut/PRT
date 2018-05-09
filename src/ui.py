"""
PyQt5 QtWidgets

User Interface classes.
"""

from multiprocessing import Process

from PyQt5.QtWidgets import (
	QDoubleSpinBox,
	QProgressBar,
    QRadioButton,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
	QLineEdit,
    QGroupBox,
    QCheckBox,
    QMenuBar,
    QToolTip,
    QWidget,
    QAction,
    QLayout,
    QWidget,
    QSlider,
    QLabel,
    QMenu,
)

from PyQt5.QtGui import (
	QImage,
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

import smopy

from osgeo import gdal

from draw import RenderArea
from img import Tiff, TiffSequence

from histogram import Histogram
from projection import (
	HRVpicture, 
	Satellite, 
	PixelZone, 
	gdal_proj_mercator,
)

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

"""
User Interface Main Window
"""
class uiMainWindow(QMainWindow):
	tifs: TiffSequence = None
	tifs_gdal: TiffSequence = None
	do_show_gdal = False

	s_area: QScrollArea = None
	img_area: RenderArea = None
	img_slider: QSlider = None
	img_info: QLabel = None
	img_posX: QLineEdit = None
	img_posY: QLineEdit = None

	slider_old_val: int = 0

	box_gdal: QCheckBox = None
	box_osm: QCheckBox = None
	sbox_gdal: QDoubleSpinBox = None

	pbar: QProgressBar = None

	def __init__(self, screen):
		super().__init__()
		self.title = "PRT"
		self.screen = screen
		self.resize_and_center(600, 400)
		self.build()

	def resize_and_center(self, w, h):
		self.left = (self.screen.size().width() - w) / 2
		self.top = (self.screen.size().height() - h) / 2
		self.width = w
		self.height = h
		self.setGeometry(self.left, self.top, self.width, self.height)

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
		old = self.slider_old_val # previous value

		l_new = old-step # new possible left value
		r_new = old+step # new possible right value

		tifs: TiffSequence = None
		if self.do_show_gdal:
			tifs = self.tifs_gdal
		else:
			tifs = self.tifs

		if value <= l_new:
			moved = True
			if value is l_new:
				tifs.shift_left()
			else:
				tifs.active(int(value/step))
		
		elif value >= r_new:
			moved = True
			if value is r_new:
				tifs.shift_right()
			else:
				tifs.active(int(value/step))

		if moved:
			self.slider_old_val = value
			_, tif = tifs.current()

			opa = 1.0
			if self.do_show_gdal:
				opa = self.sbox_gdal.value()

			self.img_area.pop()
			self.img_area.push(tif.to_QImage(), opacity=opa)
			self.img_area.update()

			self.update_img_info()

	def gdal_opacity_changed(self, value):
		info = self.img_area.pop()
		self.img_area.push(info[0], value, info[2], info[3])
		self.img_area.update()
			
	def draw_histogram(self):
		if self.tifs is None:
			return
		
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
		
		# Disable the GDAL display option
		self.box_gdal.setEnabled(False)
		self.box_gdal.setChecked(False)
		self.box_osm.setEnabled(False)

		# Clear old tifs sequence if not empty
		if self.tifs is not None:
			self.tifs.clear()

		# Save the new sequence
		self.tifs = TiffSequence(fnames)

		# Update the slider
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
		self.slider_old_val = 0
		_, tif = self.tifs.current()
		
		# Draw new image
		self.img_area.clear()
		self.img_area.push(tif.to_QImage())
		self.img_area.update()

		_h, _w = tif.shape()
		self.resize_and_center(_w+210, _h+100)
		self.update_img_info()
		
	def update_img_info(self):
		"""Update the img information text field.
		"""

		if self.tifs is None:
			return

		_, tif = self.tifs.current()
		_h, _w = tif.shape()

		# Update information label
		self.img_info.setText(
			"<b>filename</b>: "
			+tif.pname 
			+" -- <b>size</b>: "
			+str(_w)+"x"
			+str(_h)
			+" -- <b>type</b>: "
			+tif.dtype()
		)


	def sequence_as_video(self):
		"""Save our current sequence as Video.
		"""
		if self.tifs is None:
			return
		
		# for the moment, default path to video is:
		# TODO: make user choose where he wants to save the video.
		video_path = "../video/"

		# non-blocking io operation.
		Process(
			target=self.tifs.as_video,
			args=(video_path,),
			daemon=True
		).start()

	def gdal_projection(self):
		"""Proceed to a gdal meractor projection on the source sequence.
		"""
		# Parameters of the projection
		hrv = HRVpicture(11136, 11136, 1000.134, 5565.5)
		france = PixelZone(10179, 9610, 6591, 5634)
		meteosat9 = Satellite(35785831.0, 9.5, 0.0)

		# Get shape of the current sequence
		_h, _w = self.tifs.current()[1].shape()

		# The new gdal_tifs sequence
		new_paths = []

		self.pbar.setEnabled(True)
		self.pbar.setValue(0.0)
		self.pbar.setMaximum( self.tifs.img_number )

		# Iterate on pathnames of the sequence.
		# Mercator projection.
		pathnames = self.tifs.paths
		for pathname in pathnames:
			new_paths.append(
				gdal_proj_mercator(
					pathname,
					_w, _h,
					_w*2, _h*2,
					hrv,
					meteosat9, 
					france
			))
			self.pbar.setValue( self.pbar.value() + 1 )

		# Clear old tifs_gdal sequence
		if self.tifs_gdal is not None:
			self.tifs_gdal.clear()
		
		# New tifs_gdal sequence:
		self.tifs_gdal = TiffSequence(new_paths)
		self.tifs_gdal.active( self.tifs.current()[0] )
		
		# Enable display checkbox options
		self.do_show_gdal = False
		self.box_gdal.setEnabled(True)
		self.box_osm.setEnabled(True)
		self.box_osm.setCheckable(False)
		self.sbox_gdal.setValue(1.0)

		self.pbar.setValue(0.0)
		self.pbar.setEnabled(False)


	def display_gdal(self, checked: bool):
		"""When display GDAL checkbox is toggled.
		
		Arguments:
			checked {bool} -- state of the checkbox
		"""
		if checked:
			self.do_show_gdal = True
			self.box_osm.setCheckable(True)
			self.sbox_gdal.setEnabled(True)
			self.tifs_gdal.active(
				self.tifs.current()[0]
			)

			# Update display
			_, tif = self.tifs_gdal.current()
			self.img_area.clear()
			self.img_area.push(tif.to_QImage())
			self.img_area.update()
			self.sbox_gdal.setValue(1.0)

		else:
			self.do_show_gdal = False
			self.sbox_gdal.setEnabled(False)
			self.box_osm.setCheckable(False)
			self.tifs.active(
				self.tifs_gdal.current()[0]
			)

			# Update display
			_, tif = self.tifs.current()
			self.img_area.clear()
			self.img_area.push(tif.to_QImage())
			self.img_area.update()


	def display_osm(self, checked: bool):
		if checked:
			_, tif = self.tifs_gdal.current()

			# Get the bot-right corner latitude & longitude 
			# thanks to gdal.GetGeoTransform()
			src = gdal.Open(tif.pname)
			ulx, xres, _, uly, _, yres  = src.GetGeoTransform()
			lrx = ulx + (src.RasterXSize * xres)
			lry = uly + (src.RasterYSize * yres)

			# Download an OpenStreetMap Tile thanks to smopy
			# Warning: the Tile you are going to download, 
			# is bigger than the zone expected.
			_map = smopy.Map((uly, ulx, lry, lrx), z=6)
			_map.save_png("../.cache/map.png")

			# Get where are the top-left corner &
			# the bot-right corner into the OSM tile.
			x, y = _map.to_pixels(uly, ulx)
			xx, yy = _map.to_pixels(lry, lrx)

			# Compute distance between those points
			width = int((xx - x)+0.5)
			height = int((yy - y)+0.5)

			# Now we need to do some scaling & 
			# remove black pixel from the Mercator projection :
			qimage, opacity, _, _ = self.img_area.pop()

			# Scale to fit inside the OSM tile:
			qimage: QImage = qimage.smoothScaled( width, height ) 
			# Convert to RGBA, so we can add an Alpha value:
			qimage = qimage.convertToFormat(QImage.Format_ARGB32);

			# Scan our QImage :
			for h in range(0, qimage.height()):
				for w in range(0, qimage.width()):
					# Get only one component:
					# since its grey image converted to rgba, 
					# rgb values are the same.
					red = QColor( qimage.pixel(w, h) ).red()
					
					# When value is to low, set the pixel opacity to 0.
					if red is 0:
						qimage.setPixelColor(w, h, QColor(0, 0, 0, 0))

			# Now load the map, we need to add it to the RenderArea.
			map_img = QImage("../.cache/map.png")
			self.img_area.push( map_img )

			# Re-push after the map our Mercator projection image.
			# +14 pixels to fit exactly the map (visually).
			self.img_area.push( qimage, opacity, x, y+14) 

			# Also, change the SpinBox opacity value to a default one:
			self.sbox_gdal.setValue(0.8)

			# Don't forget to resize our app, so user is happy:
			self.resize_and_center(map_img.width()+210, map_img.height()+100)

		else:
			# Remove the tile image from the RenderArea
			info = self.img_area.pop()
			self.img_area.clear()
			self.img_area.push(info[0], info[1], info[2], info[3])
			self.sbox_gdal.setValue(1.0)


	###### Interface ######
	def build_left_vbox(self):
		# Information layout
		file_info = QLabel("No data.")
		file_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
		file_info.setAlignment(Qt.AlignLeft)
		file_info.setFixedWidth(9999)

		str_posX = QLabel("Position x:")
		str_posX.setAlignment(Qt.AlignRight)

		str_posY = QLabel("y:")
		str_posY.setAlignment(Qt.AlignRight)

		posX = QLineEdit()
		posX.setReadOnly(True)
		posX.setText("0")
		posX.setFixedWidth(40)
		posX.setFixedHeight(20)

		posY = QLineEdit()
		posY.setReadOnly(True)
		posY.setText("0")
		posY.setFixedWidth(40)
		posY.setFixedHeight(20)

		info_l = QHBoxLayout()
		info_l.addWidget( file_info )
		info_l.addWidget( str_posX )
		info_l.addWidget( posX )
		info_l.addWidget( str_posY )
		info_l.addWidget( posY )

		# Where we are going to draw images
		s_area = QScrollArea()
		r_area = RenderArea(self)
		s_area.setWidget(r_area)

		# The main slider
		slider = QSlider(Qt.Horizontal)
		slider.setEnabled(False) # Not usable
		slider.setFocusPolicy(Qt.StrongFocus) # Mouse & Keyboard can move it
		slider.setTickPosition(QSlider.NoTicks) # No ticks draw
		slider.valueChanged.connect(self.img_slider_moved) # What do you do when slider is moved ?
		
		# The Left Vertical Box Layout
		vbox = QVBoxLayout()
		vbox.addLayout(info_l)
		vbox.addWidget(s_area)
		vbox.addWidget(slider)

		# Usefull attributes
		self.s_area = s_area
		self.img_area = r_area
		self.img_slider = slider
		self.img_posX = posX
		self.img_posY = posY
		self.img_info = file_info

		return vbox

	def build_right_vbox(self):
		box_gdal = QCheckBox("Mercator projection")
		box_gdal.setToolTip("Display new projected tif images.")
		box_gdal.setEnabled(False)
		box_gdal.toggled.connect(self.display_gdal)

		box_osm = QCheckBox("OSM tile")
		box_osm.setToolTip("Download an OpenStreetMap tile from web API.")
		box_osm.setEnabled(False)
		box_osm.toggled.connect(self.display_osm)

		# Opacity
		l_opacity = QLabel("Opacity :")

		sbox_gdal = QDoubleSpinBox()
		sbox_gdal.setEnabled(False)
		sbox_gdal.setValue(1.0)
		sbox_gdal.setMaximum(1.0)
		sbox_gdal.setSingleStep(0.01)
		sbox_gdal.setAccelerated(True)
		sbox_gdal.setAcceptDrops(True)
		sbox_gdal.setFixedWidth(60)
		sbox_gdal.valueChanged.connect(self.gdal_opacity_changed)
		
		opacity_hbox = QHBoxLayout()
		opacity_hbox.addWidget(l_opacity)
		opacity_hbox.addWidget(sbox_gdal)
		opacity_hbox.setAlignment(Qt.AlignLeft)
		# ----------
		
		gvbox = QVBoxLayout()
		gvbox.addWidget(box_gdal)
		gvbox.addLayout(opacity_hbox)
		gvbox.addWidget(box_osm)

		gbox = QGroupBox("Display options")
		gbox.setLayout(gvbox)
		gbox.setFixedWidth(180)
		gbox.setFixedHeight(130)

		gbox2 = QGroupBox("Other options?")
		gbox2.setFixedWidth(180)

		# The multiple usage progress bar
		pbar = QProgressBar()
		pbar.setFixedWidth(180)
		pbar.setFixedHeight(20)
		pbar.setAcceptDrops(True)
		pbar.setValue(0.0)
		pbar.setEnabled(False)
		# ---------

		vbox = QVBoxLayout()
		vbox.setAlignment(Qt.AlignCenter)
		vbox.addWidget(gbox)
		vbox.addWidget(gbox2)
		vbox.addWidget(pbar)

		self.box_gdal = box_gdal
		self.box_osm = box_osm
		self.sbox_gdal = sbox_gdal
		self.pbar = pbar
		
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
		action = QAction("Open tiffs", self)
		action.setShortcut("Ctrl+O")
		action.triggered.connect(self.load_tiffs)
		return action

	def action_as_video(self):
		action = QAction("Save as video", self)
		action.triggered.connect(self.sequence_as_video)
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

	def action_gdal(self):
		action = QAction("GDAL", self)
		action.setShortcut("Ctrl+G")
		action.triggered.connect(self.gdal_projection)
		return action

	def menu_file(self):
		menu = QMenu("File", self.menuBar())
		menu.addAction(self.action_load_tiffs())
		menu.addAction(self.action_as_video())
		menu.addSeparator()
		menu.addAction(self.action_close())
		return menu

	def menu_process(self):
		menu = QMenu("Process", self.menuBar())
		menu.addAction(self.action_draw_histogram())
		menu.addAction(self.action_gdal())
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
		self.setMinimumSize(self.width, self.height)
		self.build_menu()
		self.setCentralWidget(self.build_main_widget())
