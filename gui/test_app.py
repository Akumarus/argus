"""
Управление ногой гексапода (3 сервопривода) по CANopen.

Интерфейс на Qt, 3D - pyvista (встроен в Qt-окно), график токов - pyqtgraph.

Установка:
    pip install pyvista pyvistaqt PyQt5 pyqtgraph numpy python-can canopen

Запуск:
    python hexapod_leg.py
    (параметры подключения - в блоке "настройки" ниже)

Протокол (самый простой, подгоните под прошивку):
    ПК -> устройство  RPDO1  id 0x200 + NODE : 3 x int16, углы в 0.1 градуса
    устройство -> ПК  TPDO1  id 0x180 + NODE : 3 x int16, токи в мА
"""
import math
import random
import struct
import sys
import threading
import time
from collections import deque

import numpy as np
import pyqtgraph as pg
import pyvista as pv
from pyvistaqt import QtInteractor
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
                            QGroupBox, QHBoxLayout, QLabel, QMainWindow, QPushButton,
                            QSlider, QSpinBox, QSplitter, QVBoxLayout, QWidget)

# ------------------------------- настройки ----------------------------------
DEMO = True                    # True - без железа, False - реальный CAN
CAN_INTERFACE = "socketcan"    # "socketcan" (Linux), "slcan", "pcan", "kvaser", ...
CAN_CHANNEL = "can0"           # "can0", "COM5", "PCAN_USBBUS1", ...
CAN_BITRATE = 500000
NODE_ID = 1

SEND_PERIOD_MS = 50            # не чаще чем раз в 50 мс шлём углы по CAN (20 Гц)
REFRESH_PERIOD_MS = 50         # период обновления 3D и графика
HISTORY_POINTS = 6000          # сколько точек истории токов хранить (~5 мин при 20 Гц)

ANGLE_LIMIT = 90               # диапазон углов +-90 градусов
LINK_LENGTHS = (0.5, 1.0, 1.5) # длины звеньев ноги (coxa, femur, tibia)
NAMES = ("Coxa", "Femur", "Tibia")
COLORS = ("#ff5555", "#55dd55", "#5599ff")   # цвет звена в 3D, линии графика и подписи


# ------------------------------ CAN: реальный --------------------------------
class CanLink:
    def __init__(self, interface, channel, bitrate):
        import canopen
        self.net = canopen.Network()
        self.net.connect(interface=interface, channel=channel, bitrate=bitrate)
        self.net.subscribe(0x180 + NODE_ID, self._on_tpdo)   # ждём токи
        self.net.nmt.send_command(0x01)                      # NMT Start: узлы -> Operational
        self.currents = [0, 0, 0]                            # последние токи, мА
        self.lock = threading.Lock()

    def _on_tpdo(self, cob_id, data, timestamp):             # вызывается из потока CAN
        if len(data) >= 6:
            with self.lock:
                self.currents = list(struct.unpack("<hhh", bytes(data[:6])))

    def send_angles(self, angles_deg):
        data = struct.pack("<hhh", *[int(round(a * 10)) for a in angles_deg])
        self.net.send_message(0x200 + NODE_ID, data)

    def get_currents(self):
        with self.lock:
            return list(self.currents)

    def close(self):
        self.net.disconnect()


# ------------------------------ CAN: имитация --------------------------------
class DemoLink:
    """Сервы плавно едут к заданному углу, ток ~ ошибке + шум."""

    def __init__(self):
        self.target = [0.0, 0.0, 0.0]
        self.pos = [0.0, 0.0, 0.0]
        self.currents = [0, 0, 0]
        self.lock = threading.Lock()
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while True:
            with self.lock:
                for i in range(3):
                    err = self.target[i] - self.pos[i]
                    self.pos[i] += err * 0.05
                    self.currents[i] = int((err if i != 1 else -err) * 15
                                           + 100 + random.randint(-20, 20))
            time.sleep(0.02)

    def send_angles(self, angles_deg):
        with self.lock:
            self.target = list(angles_deg)

    def get_currents(self):
        with self.lock:
            return list(self.currents)

    def close(self):
        pass


# ------------------------------ геометрия ноги -------------------------------
def leg_points(a1, a2, a3):
    """Прямая кинематика: углы в градусах -> 4 точки (основание, 3 сустава)."""
    t1, t2, t3 = np.radians([a1, a2, a3])
    l1, l2, l3 = LINK_LENGTHS
    # в плоскости ноги: r - расстояние от оси coxa, z - высота
    r1, z1 = l1, 0.0
    r2, z2 = r1 + l2 * math.cos(t2), l2 * math.sin(t2)
    r3, z3 = r2 + l3 * math.cos(t2 + t3), z2 + l3 * math.sin(t2 + t3)
    # поворот плоскости вокруг вертикальной оси на угол coxa
    return np.array([
        [0, 0, 0],
        [r1 * math.cos(t1), r1 * math.sin(t1), z1],
        [r2 * math.cos(t1), r2 * math.sin(t1), z2],
        [r3 * math.cos(t1), r3 * math.sin(t1), z3],
    ])


# ------------------------- виджет: ползунок + бокс угла ------------------------
class AngleControl(QWidget):
    """Название, текущий ток, ползунок и бокс. Ползунок и бокс связаны между собой."""
    changed = Signal()   # угол изменился (ползунком или в боксе)

    def __init__(self, name, color):
        super().__init__()
        title = QLabel(f"<b>{name}</b>")
        title.setStyleSheet(f"color: {color}")
        self.current_label = QLabel("I = 0 мА")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-ANGLE_LIMIT * 10, ANGLE_LIMIT * 10)   # шаг 0.1 градуса
        self.box = QDoubleSpinBox()
        self.box.setRange(-ANGLE_LIMIT, ANGLE_LIMIT)
        self.box.setDecimals(1)
        self.box.setSuffix(" °")
        self.box.setKeyboardTracking(False)      # из бокса - по Enter / потере фокуса

        self.slider.valueChanged.connect(self._from_slider)
        self.box.valueChanged.connect(self._from_box)

        top = QHBoxLayout()
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.current_label)
        bottom = QHBoxLayout()
        bottom.addWidget(self.slider, stretch=1)
        bottom.addWidget(self.box)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(bottom)

    def _from_slider(self, v):
        self.box.blockSignals(True)              # чтобы не зациклиться
        self.box.setValue(v / 10)
        self.box.blockSignals(False)
        self.changed.emit()

    def _from_box(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(int(round(v * 10)))
        self.slider.blockSignals(False)
        self.changed.emit()

    def value(self):
        return self.box.value()

    def set_current(self, ma):
        self.current_label.setText(f"I = {ma} мА")


# ---------------------------------- окно -------------------------------------
class Window(QMainWindow):
    def __init__(self, link):
        super().__init__()
        self.setWindowTitle("Hexapod leg")
        self.link = link

        # история токов
        self.t0 = time.time()
        self.times = deque(maxlen=HISTORY_POINTS)
        self.data = [deque(maxlen=HISTORY_POINTS) for _ in range(3)]

        # флаги: что нужно сделать на ближайшем тике таймера
        self.pose_dirty = True    # перерисовать 3D
        self.cmd_dirty = False    # отправить углы по CAN

        # --- правая часть: 3D сверху, график токов снизу (граница двигается мышью) ---
        self.view = QtInteractor(self)
        self.build_scene()
        self.plot = self.build_plot()
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.view.interactor)
        splitter.addWidget(self.plot)
        splitter.setSizes([320, 480])            # график побольше

        # --- левая панель: углы + настройки графика ---
        left = QVBoxLayout()
        self.controls = []
        for name, color in zip(NAMES, COLORS):
            ctrl = AngleControl(name, color)
            ctrl.changed.connect(self.on_angle_changed)
            left.addWidget(ctrl)
            self.controls.append(ctrl)
        left.addWidget(self.build_plot_settings())
        left.addStretch()
        left_widget = QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(330)

        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)
        main.addWidget(left_widget)
        main.addWidget(splitter, stretch=1)

        self.apply_grid()
        self.apply_y_range()

        # --- таймеры ---
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(REFRESH_PERIOD_MS)
        self.send_timer = QTimer(self)
        self.send_timer.timeout.connect(self.send_if_needed)
        self.send_timer.start(SEND_PERIOD_MS)

    # ---------------- 3D ----------------
    def build_scene(self):
        pts = leg_points(0, 0, 0)
        self.link_meshes = []
        for i, color in enumerate(COLORS):
            mesh = pv.lines_from_points(pts[i:i + 2])        # звено i: точка i -> i+1
            self.view.add_mesh(mesh, color=color, line_width=10,
                               render_lines_as_tubes=True)
            self.link_meshes.append(mesh)
        self.joints = pv.PolyData(pts[1:].copy())            # суставы - оранжевые шарики
        self.view.add_mesh(self.joints, color="orange", style="points",
                           point_size=14, render_points_as_spheres=True)
        reach = sum(LINK_LENGTHS)                            # рамка фиксирует масштаб
        self.view.add_mesh(pv.Box(bounds=(-reach, reach, -reach, reach, -reach, reach)),
                           style="wireframe", color="gray", opacity=0.3)
        self.view.add_axes()
        self.view.camera_position = "iso"

    def update_leg(self):
        pts = leg_points(*[c.value() for c in self.controls])
        for i, mesh in enumerate(self.link_meshes):
            mesh.points = pts[i:i + 2]
        self.joints.points = pts[1:]
        labels = [f"{n} ({x:.2f}, {y:.2f}, {z:.2f})"
                  for n, (x, y, z) in zip(("Hip", "Knee", "Foot"), pts[1:])]
        self.view.add_point_labels(pts[1:], labels, name="joints", font_size=12,
                                   shape=None, show_points=False,
                                   always_visible=True, render=False)
        self.view.render()

    # ---------------- график токов ----------------
    def build_plot(self):
        plot = pg.PlotWidget()
        plot.setLabel("left", "Ток, мА")
        plot.setLabel("bottom", "Время, с")
        plot.addLegend()
        self.curves = [plot.plot(pen=pg.mkPen(color, width=2), name=name)
                       for name, color in zip(NAMES, COLORS)]
        return plot

    def build_plot_settings(self):
        box = QGroupBox("График токов")
        layout = QVBoxLayout(box)

        row = QHBoxLayout()                                  # что показывать
        self.series_checks = []
        for name in NAMES:
            cb = QCheckBox(name)
            cb.setChecked(True)
            row.addWidget(cb)
            self.series_checks.append(cb)
        layout.addLayout(row)

        self.grid_check = QCheckBox("Сетка")
        self.grid_check.setChecked(True)
        self.grid_check.toggled.connect(self.apply_grid)
        layout.addWidget(self.grid_check)

        self.auto_check = QCheckBox("Автомасштаб по Y")
        self.auto_check.setChecked(True)
        self.auto_check.toggled.connect(self.apply_y_range)
        layout.addWidget(self.auto_check)

        form = QFormLayout()
        self.ymin = QSpinBox()
        self.ymin.setRange(-100000, 100000)
        self.ymin.setSingleStep(100)
        self.ymin.setValue(-2000)
        self.ymin.setSuffix(" мА")
        self.ymin.valueChanged.connect(self.apply_y_range)
        self.ymax = QSpinBox()
        self.ymax.setRange(-100000, 100000)
        self.ymax.setSingleStep(100)
        self.ymax.setValue(2000)
        self.ymax.setSuffix(" мА")
        self.ymax.valueChanged.connect(self.apply_y_range)
        self.window = QSpinBox()
        self.window.setRange(1, 300)
        self.window.setValue(10)
        self.window.setSuffix(" с")
        form.addRow("Y мин", self.ymin)
        form.addRow("Y макс", self.ymax)
        form.addRow("Окно по времени", self.window)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        self.pause_btn = QPushButton("Пауза")
        self.pause_btn.setCheckable(True)    # на паузе график можно двигать/масштабировать мышью
        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear_plot)
        buttons.addWidget(self.pause_btn)
        buttons.addWidget(clear_btn)
        layout.addLayout(buttons)
        return box

    def apply_grid(self):
        on = self.grid_check.isChecked()
        self.plot.showGrid(x=on, y=on, alpha=0.3)

    def apply_y_range(self):
        auto = self.auto_check.isChecked()
        self.ymin.setEnabled(not auto)
        self.ymax.setEnabled(not auto)
        vb = self.plot.getViewBox()
        if auto:
            vb.setAutoVisible(y=True)                        # масштаб только по видимому окну
            vb.enableAutoRange(axis=pg.ViewBox.YAxis)
        else:
            vb.setYRange(self.ymin.value(), self.ymax.value(), padding=0)

    def clear_plot(self):
        self.times.clear()
        for d in self.data:
            d.clear()
        self.t0 = time.time()
        for curve in self.curves:
            curve.setData([], [])

    # ---------------- логика ----------------
    def on_angle_changed(self):
        self.pose_dirty = True
        self.cmd_dirty = True

    def send_if_needed(self):
        """Раз в SEND_PERIOD_MS: если углы менялись - шлём последние значения."""
        if self.cmd_dirty:
            self.cmd_dirty = False
            self.link.send_angles([c.value() for c in self.controls])

    def refresh(self):
        """Раз в REFRESH_PERIOD_MS: обновляем 3D, подписи токов и график."""
        if self.pose_dirty:
            self.pose_dirty = False
            self.update_leg()

        currents = self.link.get_currents()
        for ctrl, i in zip(self.controls, currents):
            ctrl.set_current(i)
        if self.pause_btn.isChecked():
            return

        t = time.time() - self.t0
        self.times.append(t)
        for d, i in zip(self.data, currents):
            d.append(i)
        ts = np.array(self.times)
        for cb, curve, d in zip(self.series_checks, self.curves, self.data):
            curve.setVisible(cb.isChecked())
            if cb.isChecked():
                curve.setData(ts, np.array(d))
        self.plot.setXRange(t - self.window.value(), t, padding=0)

    def closeEvent(self, event):
        self.refresh_timer.stop()
        self.send_timer.stop()
        self.view.close()
        self.link.close()
        event.accept()


# ---------------------------------- main -------------------------------------
if __name__ == "__main__":
    link = DemoLink() if DEMO else CanLink(CAN_INTERFACE, CAN_CHANNEL, CAN_BITRATE)
    app = QApplication(sys.argv)
    win = Window(link)
    win.resize(1500, 800)
    win.show()
    sys.exit(app.exec())