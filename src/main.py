import sys
from PyQt5.QtWidgets import QApplication

from ui import uiMainWindow

def main():
	app = QApplication(sys.argv)
	win = uiMainWindow(app.primaryScreen())
	win.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()