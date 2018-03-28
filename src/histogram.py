from PyQt5.QtWidgets import QMainWindow

from PyQt5.QtChart import (
    QChart,
    QChartView,
    QBarSet,
    QBarSeries,
    QLineSeries,
)

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

import numpy as np

class Histogram(QMainWindow):
    def __init__(self, parent, image):
        super().__init__(parent)
        self.image = image
        self.build()
        self.show()
        
    def build(self):
        self.setWindowTitle("Histogram")
        self.setMinimumSize(400, 300)

        # 2D array -> 1D array
        img = self.image.ravel()
        histogram, bin_edges = np.histogram(img, bins='auto')

        bar_series = QBarSeries()
        bar_set = QBarSet("intensities")

        for val in histogram:
            bar_set.append(val)
        
        pen = bar_set.pen()
        pen.setColor(Qt.black)
        pen.setWidth(0.1)
        bar_set.setPen(pen)

        bar_series.append(bar_set)
        
        chart = QChart()
        chart.addSeries(bar_series)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(False)
        chart.createDefaultAxes()

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(view) 
