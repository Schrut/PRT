from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
    QMenuBar,
    QAction,
    QWidget,
)

from PyQt5.QtCore import pyqtSlot

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
Permission is hereby granted, free of charge, to any person obtaining a copy <br>\
of this software and associated documentation files (the “Software”), <br>\
to deal in the Software without restriction, including without limitation <br>\
the rights to use, copy, modify, merge, publish, distribute, sublicense, <br>\
and/or sell copies of the Software, and to permit persons to whom the Software <br>\
is furnished to do so, subject to the following conditions:<br><br>\
The above copyright notice and this permission notice shall be included in <br>\
all copies or substantial portions of the Software.<br><br>\
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, <br>\
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES <br>\
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. <br>\
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, <br>\
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, <br>\
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE <br>\
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</pre><br>\
Read more at: <a href=\"https://opensource.org/licenses/MIT\">https://opensource.org/licenses/MIT</a>"
    
    def on_clik(self):
        self.information(self.window, self.title, self.license, QMessageBox.Ok)

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

    def btn_click(self):
        QMessageBox.information(self, "test", "message test", QMessageBox.Ok, QMessageBox.Ok)

    def build(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # TODO: Add other entries & buttons
        
        # Buttons
        ## Exit button
        button_exit = QAction("Exit", self)
        button_exit.setShortcut("Ctrl+Q")
        button_exit.setStatusTip("Exit application")
        button_exit.triggered.connect(self.close)

        ## Show License button
        button_license = QAction("License", self)
        button_license.setStatusTip("Application's license")
        button_license.triggered.connect(uiLicenseWindow(self).on_clik)

        # Menus
        # Main menu
        menu = self.menuBar()

        ## File menu
        menu_file = menu.addMenu("File")
        menu_file.addAction(button_exit)

        ## About menu
        menu_about = menu.addMenu("About")
        menu_about.addAction(button_license)