from PyQt5.QtWidgets import (
	QMainWindow,
	QMessageBox,
	QScrollArea,
	QWidget,
	QMenuBar,
	QLabel,
	QAction,
	QWidget,
	QFileDialog,
)

#import glob
import time
from img import Tiff

"""
The MIT License (MIT)
https://mit-license.org/
"""
class uiLicenseWindow(QMessageBox):
	def __init__(self, window):
			super().__init__(window)
			self.window = window
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
Read more at: <a href=\"https://opensource.org/licenses/MIT\">https://opensource.org/licenses/MIT</a>"

	def on_clik(self):
			self.information(self.window, self.title, self.license, QMessageBox.Ok)

class uiOpenFile(QFileDialog):
	def __init__(self, window):
			super().__init__(window)
			self.window = window
			self.title = "Open a new file"
			
	def on_clik(self):
			fname = QFileDialog.getOpenFileName(self,
												"Open TIFF image", 
												"..",
												"Image Files (*.tiff *.tif)"
												)[0] # Take only file name

			'''
			# A mettre certainement dans une autre fonction je pense, du genre "load all dir"
			# Y'a une fonction QFileDialog.getOpenFileNames <- avec un "s", à voir ce que ça donne 
			# (https://doc.qt.io/qt-5/qfiledialog.html#getOpenFileNames)
			# 

			effectiveFileName = fileName[0]
			indice = 0
			while effectiveFileName.find("/",indice+1) != -1:
				indice = effectiveFileName.find("/",indice+1)
			list_ = glob.glob(effectiveFileName[0:indice+1]+"*.tif")
			tiff = Tiff( list_[0] )
			'''
			if fname == "": 
				return
			
			tiff = Tiff(fname)
			img_viewer = QLabel()
			img_viewer.setPixmap(tiff.to_QPixmap())
			self.window.setWidget(img_viewer)


"""
User Interface Main Window
"""
class uiMainWindow(QMainWindow):
	def __init__(self):
			super().__init__()
			self.title = "PRT"
			self.left = 200
			self.top = 200
			self.width = 1080
			self.height = 720
			self.build()

	def build(self):
			self.setWindowTitle(self.title)
			self.setGeometry(self.left, self.top, self.width, self.height)

			scroll_area = QScrollArea()
			self.setCentralWidget(scroll_area)

			# TODO: Add other entries & buttons
			
			# Buttons
			## Exit button
			button_exit = QAction("Exit", self)
			button_exit.setShortcut("Ctrl+Q")
			button_exit.setStatusTip("Exit application")
			button_exit.triggered.connect(self.close)

			## Open-File button
			button_open = QAction("Open", self)
			button_open.setShortcut("Ctrl+O")
			button_open.setStatusTip("Open an image")
			button_open.triggered.connect(uiOpenFile(scroll_area).on_clik)

			## Show License button
			button_license = QAction("License", self)
			button_license.setStatusTip("Application's license")
			button_license.triggered.connect(uiLicenseWindow(self).on_clik)

			# Menus
			# Main menu
			menu = self.menuBar()

			## File menu
			menu_file = menu.addMenu("File")
			menu_file.addAction(button_open)
			menu_file.addAction(button_exit)

			## About menu
			menu_about = menu.addMenu("About")
			menu_about.addAction(button_license)
			

