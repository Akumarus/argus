import sys
import numpy as np
import pyqtgraph as pg
from collections import deque
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSlider)

from control import Control
from plot_ctrl import PlotCtrl

class Window(QMainWindow):
    NAMES = ("Coxa", "Femur", "Tibia")
    COLORS = ("#ff5555", "#55dd55", "#5599ff")
    MAX_POINTS = 5000

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Argus Monitor")

        self.plot = pg.PlotWidget()
        self.plot.setLabel("left", "Ток, mA")
        self.plot.setLabel("bottom", "Время, с")
        self.plot.addLegend()
        self.plot.setXRange(0, 10, padding=0)
        self.plot.setYRange(-100, 100, padding=0)

        self.curves = [
            self.plot.plot(pen=pg.mkPen(c, width=2), name=n)
            for n, c in zip(self.NAMES, self.COLORS)
        ]
        for curve in self.curves:
            curve.setClipToView(True)
            curve.setDownsampling(auto=True, method="peak")
        self.t_buf = deque(maxlen=self.MAX_POINTS)
        self.y_bufs = [deque(maxlen=self.MAX_POINTS) for _ in self.NAMES]

        # Настройка графика
        plot_ctrl = PlotCtrl()
        plot_ctrl.resetClicked.connect(self.reset_view)
        plot_ctrl.clearClicked.connect(self.clear_curves)
        plot_ctrl.gridToggle.connect(self.on_grid)
        # plot_ctrl.pauseToggle.connect(self.reset_view)
        plot_ctrl.autoScaleToggle.connect(self.on_autoscale)
        

        right = QVBoxLayout()
        right.addWidget(plot_ctrl)
        right.addWidget(self.plot)
        right_widget = QWidget()
        right_widget.setLayout(right)

        left = QVBoxLayout()
        self.controls = []
        for name, color in zip(self.NAMES, self.COLORS):
            control = Control()
            left.addWidget(control)
            self.controls.append(control)
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(300)


        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.addWidget(left_widget)
        main.addWidget(right_widget)

        self._t0 = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fake_data)
        self.timer.start(20)

    def on_grid(self, on):
        if on:
            self.plot.showGrid(x=True, y=True, alpha=0.3)
        else:
            self.plot.showGrid(x=False, y=False)

    def on_autoscale(self, on):
        if on:
            self.plot.enableAutoRange()
        else:
            self.plot.disableAutoRange()

    def clear_curves(self):
        for curv in self.curves:
            curv.clear()

    def reset_view(self):
        print("reset")

    def add_sample(self, t, values):
        self.t_buf.append(t)
        for buf, v in zip(self.y_bufs, values):
            buf.append(v)
        self.redraw(t)

    def redraw(self, t_now):
        x = np.fromiter(self.t_buf, dtype=float)
        for curve, buf in zip(self.curves, self.y_bufs):
            curve.setData(x, np.fromiter(buf, dtype=float))

        # бегущее окно: последние WINDOW_S секунд
        left = max(0.0, t_now - self.WINDOW_S)
        self.plot.setXRange(left, left + self.WINDOW_S, padding=0)
        print(1)

    def fake_data(self):
        self._t0 += 0.02
        t = self._t0
        self.add_sample(t, [
            60 * np.sin(2 * t),
            40 * np.sin(3 * t + 1),
            80 * np.sin(t + 2),
        ])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    win = Window()
    win.resize(1500, 800)
    win.show()
    sys.exit(app.exec()) 