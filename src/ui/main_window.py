"""
PyQt5 QtWidgets

User Interface classes.
"""

from multiprocessing import Process
from time import time

from PyQt5.QtWidgets import (
    QDoubleSpinBox,
	QMessageBox,
    QProgressBar,
    QRadioButton,
	QInputDialog,
    QMainWindow,
    QFileDialog,
    QScrollArea,
    QSizePolicy,
    QPushButton,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
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
	QRect,
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

from .license import uiLicenseWindow
from .view import ResultWindow
from lbp import lbp
from equalize import histogram_equalization
from alignment import alignement
from kmeans import kmeans

"""
User Interface Main Window
"""
class uiMainWindow(QMainWindow):

	# TIFFS SEQUENCES:
	tifs: TiffSequence = None # source Files.
	tifs_gdal: TiffSequence = None # source files after projection.
	do_show_gdal = False
	do_show_osm = False

	# OpenStreetMap
	osm_action: QAction = None
	osm_w: int = 0
	osm_h: int = 0
	osm_x: int = 0
	osm_y: int = 0
	
	# Usefull widgets
	s_area: QScrollArea = None
	img_area: RenderArea = None
	img_slider: QSlider = None
	img_info: QLabel = None
	img_posX: QLineEdit = None
	img_posY: QLineEdit = None
	box_gdal: QCheckBox = None
	box_osm: QCheckBox = None
	sbox_gdal: QDoubleSpinBox = None
	pbar: QProgressBar = None
	cbox_color: QComboBox = None
	crop_button: QPushButton = None

	# slider old value/index
	slider_old_val: int = 0

	def __init__(self, screen):
		super().__init__()
		self.title = "PRT"
		self.screen = screen
		self.resize_and_center(800, 600)
		self.build()

	def resize_and_center(self, w, h):
		ssize = self.screen.size()
		sw = ssize.width()
		sh = ssize.height()

		self.left = (sw - w) / 2
		self.top = (sh - h) / 2
		self.width = w
		self.height = h

		self.setGeometry(self.left, self.top, self.width, self.height)

	######################################################################
	######################################################################
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
			
			# If OSM display is ON
			if self.do_show_osm:
				# Scale image to fit the map
				image = tif.to_QImage().scaled(
					self.osm_w, self.osm_h,
					Qt.IgnoreAspectRatio,
					Qt.SmoothTransformation
				)
				self.img_area.push(image, opa, self.osm_x, self.osm_y+14)

			else:
				self.img_area.push(tif.to_QImage(), opacity=opa)

			self.img_area.update()
			self.update_img_info()

	def gdal_opacity_changed(self, value):
		info = self.img_area.pop()
		self.img_area.push(info[0], value, info[2], info[3])
		self.img_area.update()
			
	def draw_histogram(self):
		# Get the right sequence:
		tifs: TiffSequence = None
		if self.do_show_gdal:
			tifs = self.tifs_gdal
		else:
			tifs = self.tifs

		if tifs is None:
			return
		
		_, tif = tifs.current()
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
		self.osm_action.setEnabled(False)

		# Clear old tifs sequence if not empty
		if self.tifs is not None:
			self.tifs.clear()

		# Save the new sequence
		self.tifs = TiffSequence(fnames)

		## SLIDER:
		size = self.tifs.size()
		width = self.img_slider.width()

		# Step
		step = int(width/size)
		if step is 0:
			step = 1
		
		# Slider parameters
		self.img_slider.setEnabled(True)
		self.img_slider.setValue(0)
		self.img_slider.setMaximum( (size-1)*step )
		self.img_slider.setSingleStep(step)
		self.img_slider.setTickInterval(step)
		self.img_slider.setTickPosition(QSlider.TicksBelow)

		# Reset old position.
		self.slider_old_val = 0

		# Draw new image
		_, tif = self.tifs.current()
		self.img_area.clear()
		self.img_area.push(tif.to_QImage())
		self.img_area.update()
		self.update_img_info()

		# Resize app
		_h, _w = tif.shape()
		self.resize_and_center(_w+206, _h+95)
		
	def update_img_info(self):
		"""Update the img information text field.
		"""
		# Get the right sequence
		tifs: TiffSequence = None
		if self.do_show_gdal:
			tifs = self.tifs_gdal
		else:
			tifs = self.tifs

		# Check if not null
		if tifs is None:
			return

		idx, tif = tifs.current()
		_h, _w = tif.shape()

		# Get the zoom percentage
		zoom_per = self.img_area.zlevel * self.img_area.zstep * 100

		# Update information label
		self.img_info.setText(
			"<b>filename</b>: "
			+tif.pname 
			+" ~ <b>size</b>: "
			+str(_w)+"x"
			+str(_h)
			+" ~ <b>type</b>: "
			+tif.dtype()
			+" ~ <b>scale</b>: "
			+str(zoom_per)+"%"
			+" ~ <b>index</b>: "+str(idx+1)+"/"
			+str(tifs.img_number)
		)

	def gdal_projection(self):
		"""Proceed to a gdal meractor projection on the source sequence.
		"""
		# If sequence is null
		if self.tifs is None:
			return

		# Parameters of the projection
		hrv = HRVpicture(11136, 11136, 1000.134, 5565.5) # High Resolution Visible
		france = PixelZone(10179, 9610, 6591, 5634) # France croped region, inside HRV
		meteosat9 = Satellite(35785831.0, 9.5, 0.0) # Satellite height, lon & lat

		# Get shape of the current sequence.
		# Assuming that the whole sequence as the same size.
		_, tif = self.tifs.current()
		_h, _w = tif.shape()

		# The new gdal_tifs sequence
		new_paths = []

		# Enable progress bar
		self.pbar.setEnabled(True)
		self.pbar.setValue(0.0)
		self.pbar.setMaximum( self.tifs.img_number )

		# Iterate on pathnames of the sequence.
		for pathname in self.tifs.paths:
			new_paths.append(
				# Mercator projection
				gdal_proj_mercator(
					pathname,
					_w, _h,
					_w*2, _h*2,
					hrv,
					meteosat9, 
					france
			))
			# Update progress bar
			self.pbar.setValue( self.pbar.value() + 1 )

		# Clear old tifs_gdal sequence
		if self.tifs_gdal is not None:
			self.tifs_gdal.clear()
		
		# New tifs_gdal sequence:
		self.tifs_gdal = TiffSequence(new_paths)
		
		# Setup display options:
		self.do_show_gdal = False
		self.box_gdal.setEnabled(True)
		self.sbox_gdal.setValue(1.0)

		# Reset progress bar
		self.pbar.setValue(0.0)
		self.pbar.setEnabled(False)

		self.osm_action.setEnabled(True)


	def display_gdal(self, checked: bool):
		"""When display GDAL checkbox is toggled.
		
		Arguments:
			checked {bool} -- state of the checkbox
		"""
		# Disable ROI display
		self.img_area.draw_rect = False

		if checked:
			idx, _ = self.tifs.current()

			self.do_show_gdal = True
			self.box_osm.setCheckable(True)
			self.sbox_gdal.setEnabled(True)
			self.sbox_gdal.setValue(1.0) # Reset opacity to 1.0

			# Active the good image.
			self.tifs_gdal.active(idx)
			_, tif = self.tifs_gdal.current()

			# Update display
			self.img_area.clear() # Erase all
			self.img_area.push(tif.to_QImage())
			self.img_area.zlevel = 2
			self.img_area.update()
			self.update_img_info()

			# Update app size
			zoom = self.img_area.zoom()
			_h, _w = tif.shape()
			self.resize_and_center((_w*zoom)+206, (_h*zoom)+95)

		else:
			idx, _ = self.tifs_gdal.current()

			self.do_show_gdal = False
			self.do_show_osm = False
			self.sbox_gdal.setEnabled(False)
			self.box_osm.setCheckable(False)
			self.tifs.active(idx)

			# Update display
			_, tif = self.tifs.current()
			self.img_area.clear()
			self.img_area.push(tif.to_QImage())
			self.img_area.zlevel = 4
			self.img_area.update()
			self.update_img_info()
			
			# Update app size
			_h, _w = tif.shape()
			self.resize_and_center(_w+206, _h+95)


	def display_osm(self, checked: bool):
		"""When OSM Tile display option is checked.
		"""
		self.do_show_osm = checked
		self.img_area.draw_rect = False

		if checked:
			# In this state, the meractor projection is currently displayed.
			# The OSM tile is already downloaded.
			# Now, we need to add OSM tile to the RenderArea.
			# Then, add a pre-treatment to the Mercator projection (scaling, ...)

			self.sbox_gdal.setValue(0.8) # Opacity

			image, opacity, x, y = self.img_area.pop() # pop image projection

			# Insert the map into the stack
			imap = QImage("../.cache/osm/map.png")
			self.img_area.push(imap, 1.0, 0, 0)

			# Scale image to fit the map
			image = image.scaled(
				self.osm_w, self.osm_h,
				Qt.IgnoreAspectRatio,
				Qt.SmoothTransformation
			)
			
			self.img_area.push(image, opacity, self.osm_x, self.osm_y+14) # ?? +14 to fit exactly the map

			self.img_area.zlevel = 4
			self.img_area.update()

			self.update_img_info()
			self.resize_and_center(imap.width()+206, imap.height()+95)

		else:
			self.sbox_gdal.setValue(1.0) # Opacity

			# Remove OSM tile from the RenderArea
			_, opacity, _, _ = self.img_area.pop() # Projected image
			self.img_area.clear() # Remove all

			# Since we don't need scaling ..., 
			# just push the raw projected image.
			_, tif = self.tifs_gdal.current() 
			self.img_area.push(tif.to_QImage(), opacity, 0, 0)
			self.img_area.zlevel = 2
			self.img_area.update()

			self.update_img_info()

			zoom = self.img_area.zoom()
			_h, _w = tif.shape()
			self.resize_and_center((_w*zoom)+206, (_h*zoom)+95)

	def download_osm(self):
		"""Download an OpenStreetMap tile from the web API.
		"""
		if self.tifs_gdal is None:
			return

		self.pbar.setEnabled(True)
		self.pbar.setMaximum(100)
		self.pbar.setValue(20)

		old, tif = self.tifs_gdal.current()

		# Get the bot-right corner latitude & longitude 
		# thanks to gdal.GetGeoTransform()
		src = gdal.Open(tif.pname)
		ulx, xres, _, uly, _, yres  = src.GetGeoTransform()
		lrx = ulx + (src.RasterXSize * xres)
		lry = uly + (src.RasterYSize * yres)

		self.pbar.setValue(40)
                
		try:
			# Download an OpenStreetMap Tile thanks to smopy
			# Warning: the Tile you are going to download, 
			# is bigger than the zone expected.
			_map = smopy.Map((uly, ulx, lry, lrx), z=6)

			self.pbar.setValue(80)

			# Save image
			path = "../.cache/osm/"
			if not os.path.exists(path):
				os.makedirs(path)
		
			_map.save_png(path+"map.png")

			# Get top-left & bot-righet corners pixels coordinates:
			x, y = _map.to_pixels(uly, ulx)
			xx, yy = _map.to_pixels(lry, lrx)

		except:
			
			## ERROR Dialog Message
			ok = QMessageBox.warning(
				self,
				"Error: failed to download.",
				"Download of tiles from OpenStreetMap failed.<br>\
				You should check your internet connection.",
				QMessageBox.Ok
			)

			self.pbar.setValue(0)
			self.pbar.setEnabled(False)
			return

		# Compute distance between those points:
		# Those distances, will be the size of our mercator 
		# projections once they are scaled.
		self.osm_w = int((xx - x)+0.5)
		self.osm_h = int((yy - y)+0.5)
		self.osm_x = x
		self.osm_y = y

		self.pbar.setValue(100)
		self.box_osm.setEnabled(True)
		# If the mercator projection is already displayed while downloading Tile
		if self.do_show_gdal:
			self.box_osm.setCheckable(True)
		else:
			self.box_osm.setCheckable(False)
		
		self.pbar.setEnabled(False)
		self.pbar.setValue(0)

	def cbox_color_vchanged(self, value):
		"""When ROI color combox box value change.
		
		Arguments:
			value {Qt.GlobalColor index} -- The enum value of the color.
		"""
		color = self.cbox_color.itemData(value)
		self.img_area.rect_color = Qt.GlobalColor( color )
		self.img_area.update()


	def make_a_crop(self):
		"""Create new PNG images of the croped sequence.
		"""
		if self.img_area.draw_rect:
			self.pbar.setEnabled(True)
			
			path = "../.cache/crop/" + str(int(time())) +"/"
			if not os.path.exists(path):
				os.makedirs(path)

			# pathnames of all the new croped images.
			paths = []

			# Select the current tiff sequence
			tifs: TiffSequence = None
			if self.do_show_gdal:
				tifs = self.tifs_gdal
			else:
				tifs = self.tifs

			self.pbar.setMaximum(tifs.img_number)

			tifs.active(0)

			for i in range(0, tifs.img_number):
				# Pop the previous image on the stack
				self.img_area.pop()

				# Opacity
				opa = 1.0
				if self.do_show_gdal:
					opa = self.sbox_gdal.value()

				_, tif = tifs.current()
				
				# If OSM display is ON
				if self.do_show_osm:
					# Scale image to fit the map
					image = tif.to_QImage().scaled(
						self.osm_w, self.osm_h,
						Qt.IgnoreAspectRatio,
						Qt.SmoothTransformation
					)
					self.img_area.push(image, opa, self.osm_x, self.osm_y+14)

				else:
					self.img_area.push(tif.to_QImage(), opacity=opa)

				# name without extension (.tif or .tiff)
				name = os.path.splitext(tif.name)[0]
				name = path + name + ".png"
				paths.append( name )
				self.img_area.save(name, True)

				self.pbar.setValue( self.pbar.value() + 1 )
				tifs.shift_right()

			self.pbar.setValue(0)
			self.pbar.setEnabled(False)

			self.img_slider.setValue( tifs.img_number * self.img_slider.singleStep() )

			## Display results
			ResultWindow(self, paths)

	def apply_lbp(self):
		if self.tifs is None:
			return

		radius = QInputDialog().getInt(
			self,
			"Local binary patterns",
			"Radius",
			1, 1,
		)

		if radius[1] is False:
			return

		paths = lbp(self.tifs.paths, radius[0], self.pbar)
		ResultWindow(self, paths)

	def apply_histo_equalization(self):
		if self.tifs is None:
			return

		paths = histogram_equalization(self.tifs.paths, self.pbar)
		ResultWindow(self, paths)

	def apply_alignement(self):
		if self.tifs is None:
			return

		paths = alignement(self.tifs.paths, self.pbar)
		ResultWindow(self, paths)

	def apply_kmeans(self):
		if self.tifs is None:
			return

		K = QInputDialog.getInt(
			self,
			"K-Means",
			"Number of clusters",
			4, 1
		)

		if K[1] is False:
			return

		paths = kmeans(self.tifs.paths, K[0], self.pbar)
		ResultWindow(self, paths)

	######################################################
	######################################################
	###### Interface ######
	def build_left_vbox(self):
		# Information layout
		file_info = QLabel("No data.")
		file_info.setTextInteractionFlags(Qt.TextSelectableByMouse)
		file_info.setAlignment(Qt.AlignLeft)

		info_l = QHBoxLayout()
		info_l.addWidget( file_info )

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
		self.img_info = file_info

		return vbox

	def build_right_vbox(self):
		# Position X|Y Info
		str_posX = QLabel("x:")
		str_posX.setFixedWidth(15)
		str_posX.setAlignment(Qt.AlignRight)

		str_posY = QLabel("y:")
		str_posY.setFixedWidth(15)
		str_posY.setAlignment(Qt.AlignRight)

		posX = QLineEdit()
		posX.setReadOnly(True)
		posX.setText("0")
		posX.setFixedWidth(50)
		posX.setFixedHeight(20)

		posY = QLineEdit()
		posY.setReadOnly(True)
		posY.setText("0")
		posY.setFixedWidth(50)
		posY.setFixedHeight(20)

		pos_l = QHBoxLayout()
		pos_l.addWidget( str_posX )
		pos_l.addWidget( posX )
		pos_l.addWidget( str_posY )
		pos_l.addWidget( posY )
		pos_l.setContentsMargins(0, 25, 0, 10)

		### DISPLAY OPTIONS
		box_gdal = QCheckBox("Mercator projection.")
		box_gdal.setToolTip("Display new projected tif images")
		box_gdal.setEnabled(False)
		box_gdal.toggled.connect(self.display_gdal)

		box_osm = QCheckBox("OSM tile.")
		box_osm.setToolTip("Display OSM Tile behind projection")
		box_osm.setEnabled(False)
		box_osm.toggled.connect(self.display_osm)

		# Opacity
		label_opacity = QLabel("Opacity :")

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
		opacity_hbox.addWidget(label_opacity)
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
		gbox.setFixedHeight(150)
		### ------------

		### ROI OPTIONS
		cbox_color = QComboBox()
		cbox_color.setSizeAdjustPolicy(QComboBox.AdjustToContents)
		cbox_color.addItem('Yellow', Qt.yellow)
		cbox_color.addItem('Red', Qt.red)
		cbox_color.addItem('Green', Qt.green)
		cbox_color.addItem('Blue', Qt.blue)
		cbox_color.activated.connect(self.cbox_color_vchanged)

		label_color = QLabel("Color : ")

		layout_color = QHBoxLayout()
		layout_color.addWidget(label_color)
		layout_color.addWidget(cbox_color)
		layout_color.setAlignment(Qt.AlignHCenter)

		crop_button = QPushButton("Make a crop")
		crop_button.clicked.connect(self.make_a_crop)

		layout_crop = QHBoxLayout()
		layout_crop.addWidget(crop_button)
		layout_crop.setAlignment(Qt.AlignHCenter)

		gvbox2 = QVBoxLayout()
		gvbox2.addLayout(layout_color)
		gvbox2.addLayout(layout_crop)

		gbox2 = QGroupBox("ROI options")
		gbox2.setLayout( gvbox2 )
		gbox2.setFixedHeight(100)

		### Future options?
		gbox3 = QGroupBox("")
		gvbox3 = QVBoxLayout()
		gbox3.setLayout( gvbox3 )
		### ------------

		# The multiple usage progress bar
		pbar = QProgressBar()
		pbar.setFixedWidth(180)
		pbar.setFixedHeight(20)
		pbar.setAcceptDrops(True)
		pbar.setValue(0.0)
		pbar.setEnabled(False)
		# ---------

		vbox = QVBoxLayout()
		vbox.addLayout(pos_l)
		vbox.setAlignment(Qt.AlignCenter)
		vbox.addWidget(gbox)
		vbox.addWidget(gbox2)
		vbox.addWidget(gbox3)
		vbox.addWidget(pbar)

		self.box_gdal = box_gdal
		self.box_osm = box_osm
		self.sbox_gdal = sbox_gdal
		self.pbar = pbar
		self.cbox_color = cbox_color

		self.img_posX = posX
		self.img_posY = posY

		self.crop_b = crop_button
		
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
	
	###################################################
	###################################################
	####### MENU #######
	### ACTIONS
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
		action = QAction("GDAL Mercator projection", self)
		action.setShortcut("Ctrl+G")
		action.triggered.connect(self.gdal_projection)
		return action

	def action_dl_osm_tile(self):
		action = QAction("OpenStreetMap Tile", self)
		action.triggered.connect(self.download_osm)
		action.setEnabled(False)
		self.osm_action = action
		return action

	def action_lbp(self):
		action = QAction("Local Binary Patterns ", self)
		action.triggered.connect(self.apply_lbp)
		return action

	def action_histo_equalization(self):
		action = QAction("Histogram equalization", self)
		action.triggered.connect(self.apply_histo_equalization)
		return action

	def action_alignment(self):
		action = QAction("Alignement", self)
		action.triggered.connect(self.apply_alignement)
		return action

	def action_kmeans(self):
		action = QAction("K-Means", self)
		action.triggered.connect(self.apply_kmeans)
		return action
	
	### --------------------------------------------------------

	### MENU BAR MENUS:
	def menu_file(self):
		menu = QMenu("File", self.menuBar())
		menu.addAction(self.action_load_tiffs())
		menu.addSeparator()
		menu.addAction(self.action_close())
		return menu

	def menu_process(self):
		menu = QMenu("Process", self.menuBar())
		menu.addAction(self.action_draw_histogram())
		menu.addAction(self.action_gdal())
		menu.addAction(self.action_histo_equalization())
		menu.addAction(self.action_alignment())
		menu.addAction(self.action_lbp())
		menu.addAction(self.action_kmeans())
		return menu

	def menu_download(self):
		menu = QMenu("Download", self.menuBar())
		menu.addAction(self.action_dl_osm_tile())
		return menu
	
	def menu_about(self):
		menu = QMenu("About", self.menuBar())
		menu.addAction(self.action_show_license())
		return menu

	def build_menu(self):
		menu = self.menuBar()
		menu.addMenu(self.menu_file())
		menu.addMenu(self.menu_process())
		menu.addMenu(self.menu_download())
		menu.addMenu(self.menu_about())
	### --------------------------------------------------
	#####################

	###### BUILD ALL ######
	def build(self):
		self.setWindowTitle(self.title)
		self.setMinimumSize(self.width, self.height)
		self.build_menu()
		self.setCentralWidget(self.build_main_widget())
