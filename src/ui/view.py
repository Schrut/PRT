from PyQt5.QtWidgets import (
    QMainWindow,
    QScrollArea,
    QToolButton, 
    QGridLayout, 
    QHBoxLayout, 
    QVBoxLayout,
    QShortcut,
    QWidget, 
    QLabel,
)

from PyQt5.QtGui import QImage, QKeySequence
from PyQt5.QtCore import Qt

from draw import RenderArea

class ResultWindow(QMainWindow):
    def __init__(self, parent: QWidget, paths):
        super().__init__(parent)
        self.parent = parent
        self.title = "Result(s)"
        self.area = RenderArea(None)

        self.paths = paths
        self.index = 0

        self.build()
        self.show()

    def shift_left(self):
        if self.index > 0:
            self.index -= 1

        self.area.pop()
        self.area.push(QImage(self.paths[self.index]))
        self.area.update()

        self.update_info(self.paths[self.index])

    def shift_right(self):
        if self.index < (len(self.paths)-1):
            self.index += 1

        self.area.pop()
        self.area.push(QImage(self.paths[self.index]))
        self.area.update()

        self.update_info(self.paths[self.index])

    def update_info(self, text):
        self.info.setText(
            text
            +" ~ "
            +str(self.index+1)
            +"/"
            +str(len(self.paths)) 
        )

    def build_info(self):
        self.info = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.info)

        return layout

    def build_draw_area(self):
        s_area = QScrollArea()
        s_area.setWidget(self.area)

        image = QImage(self.paths[self.index])
        self.area.push(image)
        self.update_info(self.paths[self.index])
        
        geo = self.geometry()
        self.setGeometry(geo.x(), geo.y(), image.width()+20, image.height()+74)

        layout = QHBoxLayout()
        layout.addWidget(s_area)

        return layout

    def build_buttons(self):
        arrow_left = QToolButton()
        arrow_left.setAutoRepeatDelay(1)
        arrow_left.setAcceptDrops(True)
        arrow_left.setAutoRepeat(True)
        arrow_left.setArrowType(Qt.LeftArrow)
        arrow_left.clicked.connect(self.shift_left)

        arrow_right = QToolButton()
        arrow_left.setAutoRepeatDelay(1)
        arrow_right.setAcceptDrops(True)
        arrow_right.setAutoRepeat(True)
        arrow_right.setArrowType(Qt.RightArrow)
        arrow_right.clicked.connect(self.shift_right)
        
        layout = QHBoxLayout()
        layout.addWidget( arrow_left )
        layout.addWidget( arrow_right)
        layout.setAlignment( Qt.AlignHCenter )

        return layout
        
    def build_grid(self):
        grid = QGridLayout()
        grid.addLayout(self.build_info(), 0, 0)
        grid.addLayout(self.build_draw_area(), 1, 0)
        grid.addLayout(self.build_buttons(), 2, 0)
        return grid

    def build(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(200, 200)
        self.setGeometry(self.parent.geometry())

        # Close when ctrl+w is triggered
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)
        
        widget = QWidget()
        widget.setLayout(self.build_grid())
        self.setCentralWidget(widget)