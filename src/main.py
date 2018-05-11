import sys
import shutil

from PyQt5.QtWidgets import QApplication
from ui.main_window import uiMainWindow

def main():
    # Remove the .cache directory
    shutil.rmtree("../.cache", ignore_errors=True)

    app = QApplication(sys.argv)
    win = uiMainWindow(app.primaryScreen())
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()