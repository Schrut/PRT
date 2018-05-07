"""
PyQt5 QtWidgets

User Interface classes.
"""

from multiprocessing import Process

from PyQt5.QtWidgets import (
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
    QGroupBox,
    QCheckBox,
    QMenuBar,
    QToolTip,
    QWidget,
    QAction,
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

from draw import RenderArea
from img import Tiff, TiffSequence

from histogram import Histogram
from projection import (
	HRVpicture, 
	Satellite, 
	PixelZone, 
	gdal_translate, 
	gdal_warp,
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

	img_slider_old: int = 0

	box_gdal: QCheckBox = None
	
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
		old = self.img_slider_old # previous value

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
			self.img_slider_old = value
			_, tif = tifs.current()

			_map = smopy.Map((
				51.5855835, 
				-6.5710541, 
				42.0220060, 
				8.6532580
			), z=6)

			_map.save_png('../france.png')

			self.img_area.clear()
			_h, _w = tif.shape()

			map_img = QImage('../france.png')


			self.img_area.push(
				tif.to_QImage().smoothScaled(_w, _h),
				opacity=0.8
			)
			self.img_area.push(map_img, opacity=1.0)
			
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
		
		_h, _w = tif.shape()
		
		# Draw new image
		self.img_area.clear()
		self.img_area.push(tif.to_QImage())
		self.img_area.update()

		# Fix maximum size of the scroll area
		self.s_area.setMaximumSize(_w+2, _h+2)
		
		# New size of the window
		new_h = _h+2 + self.menuBar().height() + self.img_slider.height() + 30
		new_w = _w+2 + self.centralWidget().layout().itemAt(1).geometry().width() + 25
		self.resize_and_center(new_w, new_h)

	def sequence_as_video(self):
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
		print("GDAL projection")

		tr_o_path = "../.cache/gdal/translate/"
		wr_o_path = "../.cache/gdal/warp/"

		hrv = HRVpicture(11136, 11136, 1000.134, 5565.5)
		france = PixelZone(10179, 9610, 6591, 5634)
		meteosat9 = Satellite(35785831.0, 9.5, 0.0)

		old = self.tifs.current()[0]
		self.tifs.active(0)

		self.tifs_gdal = TiffSequence([])

		idx, tif = self.tifs.current()
		while idx is not self.tifs.img_number-1:
			gdal_translate(tif, tr_o_path, hrv, meteosat9, france)
			tif_tr = Tiff(tr_o_path+tif.name)
			gdal_warp(tif_tr, (1916, 1140), wr_o_path, hrv, meteosat9, france)
			
			self.tifs_gdal.paths.append(wr_o_path+tif.name)
			self.tifs_gdal.img_number += 1

			self.tifs.shift_right()
			idx, tif = self.tifs.current()

		self.tifs_gdal.active(0)
		self.tifs.active(old)
		
		self.do_show_gdal = False
		self.box_gdal.setEnabled(True)

	def display_gdal(self, checked: bool):
		if checked:
			self.do_show_gdal = True
			self.tifs_gdal.active(
				self.tifs.current()[0]
			)

		else:
			self.do_show_gdal = False
			self.tifs.active(
				self.tifs_gdal.current()[0]
			)

	###### Interface ######
	def build_left_vbox(self):
		# Where we are going to draw images
		s_area = QScrollArea()
		r_area = RenderArea()
		s_area.setWidget(r_area)

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
		self.s_area = s_area
		self.img_area = r_area
		self.img_slider = slider

		return vbox

	def build_right_vbox(self):
		box_gdal = QCheckBox("GDAL projection")
		box_gdal.setToolTip("Display new projected tif images.")
		box_gdal.setEnabled(False)
		box_gdal.toggled.connect(self.display_gdal)

		box_osm = QCheckBox("OSM tile")
		box_osm.setToolTip("Download an OpenStreetMap tile from web API.")

		gvbox = QVBoxLayout()
		gvbox.addWidget(box_gdal)
		gvbox.addWidget(box_osm)

		gbox = QGroupBox("Display options")
		gbox.setLayout(gvbox)
		gbox.setMaximumHeight(100)

		gbox2 = QGroupBox("Other options?")

		vbox = QVBoxLayout()
		vbox.addWidget(gbox)
		vbox.addWidget(gbox2)

		self.box_gdal = box_gdal
		
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
