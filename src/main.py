"""
    Tips for Visual Studio Code:
        use `Python` extension from Microsoft with `pylint`.
        use `Python Docstring` extension from Nils Werner.
"""

import sys
import time
from PyQt5.QtWidgets import QApplication

from ui import uiMainWindow

def main():
		app = QApplication(sys.argv)
		win = uiMainWindow(app.primaryScreen())
		win.show()
		sys.exit(app.exec_())

if __name__ == "__main__":
		main()