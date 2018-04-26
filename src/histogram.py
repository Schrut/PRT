from PyQt5.QtWidgets import (
    QMainWindow,
    QShortcut,
)

from PyQt5.QtChart import (
    QChart,
    QChartView,
    QBarSet,
    QBarSeries,
    QValueAxis,
)

from PyQt5.QtGui import (
    QPainter,
    QKeySequence,
)

from PyQt5.QtCore import Qt

import numpy as np

class Histogram(QMainWindow):
    def __init__(self, parent, image, name=""):
        super().__init__(parent)
        self.image = image
        self.name = name
        self.build()
        self.show()

    def build(self):
        self.setWindowTitle("Histogram - "+self.name)
        self.setMinimumSize(400, 300)

        # Close when ctrl+w is triggered
        QShortcut(QKeySequence("Ctrl+W"), self, self.close)

        # 2D array -> 1D array
        img = self.image.ravel()
        
        # Process histogram
        histogram, bin_edges = np.histogram(img, bins='auto')

        bar_series = QBarSeries()
        bar_ = QBarSet("")

        # Append values
        for val in histogram:
            bar_.append(val)

        pen = bar_.pen()
        pen.setColor(Qt.black)
        pen.setWidth(0.1)
        bar_.setPen(pen)
        
        # Append bar to the bar series
        bar_series.append(bar_)
        
        # Chart object
        chart = QChart()
        chart.addSeries(bar_series)

        # Active animation
        chart.setAnimationOptions(QChart.SeriesAnimations)

        # Do not show title
        chart.legend().setVisible(False)

        # Draw Axes, with [min, max]
        # Y axis
        h_max = histogram.max()
        axis_y = QValueAxis()
        axis_y.setRange(0, h_max)

        # X axis
        be_max = bin_edges.max()
        be_min = bin_edges.min()
        axis_x = QValueAxis()
        axis_x.setRange(be_min, be_max)

        # Add axis to chart + rendering
        chart.addAxis(axis_x, Qt.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignLeft)

        view = QChartView(chart)
        view.setRenderHint(QPainter.Antialiasing)
        
        self.setCentralWidget(view)