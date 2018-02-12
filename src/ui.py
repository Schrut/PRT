from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QWidget,
    QMenuBar,
    QLabel,
    QAction,
    QWidget,
)

from img import Image

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

        #### Loading image, test
        
        tiff_img = Image('../tif/20170407080916_MSG2.tif')
        #tiff_img = Image('../tif/20170407054917_MSG2.tif')
        #tiff_img = Image('../Lenna.png')

        img_viewer = QLabel()
        pixmap = tiff_img.cvt_to_QPixmap()
        img_viewer.setPixmap(pixmap)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(img_viewer)

        self.setCentralWidget(scroll_area)

