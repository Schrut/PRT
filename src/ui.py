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

	def get_tiffs(self):
		"""Load tiffs files names into memory.

		TODO:
			Une classe qui centralise le travail sur la séquence de Tiff (faire quelque chose de fnames):
				-> LA CLASSE uiMainWindow NE doit PLUS S'OCCUPER de SAUVEGARDER en mémoire les IMAGES.
					----> juste appeler les bonnes fonctions pour afficher la bonne image.
					
				-> savoir qu'elle est l'image affichée
				-> charger en mémoire l'image précédente et suivante (permet de switch rapidement 
					-- attention aux exceptions de bords et de longueur de séquence)
				-> permettra de rendre facile l'implémentation de Slider
				-> KeyEvent (touches flêches) à implémenter pour le slider.
		"""


		""" Pour le moment: lit une séquence, 
		mais n'affiche que la première.
		"""

		fnames = QFileDialog.getOpenFileNames(
			self, 
			"Load a Tiff sequence", 
			"..",
			"Images Files (*.tiff *.tif)"
		)[0]

		if not fnames:
			return
		
		self.curr_tiff = Tiff(fnames[0])
		self.curr_tiff.draw_into(self.centralWidget())

	def build(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setMinimumSize(self.width, self.height)

		scroll_area = QScrollArea()
		self.setCentralWidget(scroll_area)

		# Buttons
		## Exit button
		button_exit = QAction("Exit", self)
		button_exit.setShortcut("Ctrl+Q")
		button_exit.triggered.connect(self.close)

		## Open-Files button
		button_open = QAction("Open Tiffs", self)
		button_open.setShortcut("Ctrl+O")
		button_open.triggered.connect(self.get_tiffs)

		## Show License button
		button_license = QAction("License", self)
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
		menu_file.addSeparator()
		menu_file.addAction(button_exit)

		## Process menu
		menu_process = menu.addMenu("Process")
		menu_process.addAction(button_process_gdal)
		menu_process.addAction(button_process_histo)

		## About menu
		menu_about = menu.addMenu("About")
		menu_about.addAction(button_license)

		## Test
		#_map = smopy.Map((42, 0, 43, 0), z=7)
		#_map.save_png('france.png')
