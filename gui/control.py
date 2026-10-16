from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QWidget, QDoubleSpinBox, QSlider, QVBoxLayout, QHBoxLayout, QLabel


class Control(QWidget):
    ANGLE_LIMIT = 90
    changed = Signal()

    def __init__(self):
        super().__init__()

        self.box = QDoubleSpinBox()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-self.ANGLE_LIMIT * 10, self.ANGLE_LIMIT * 10)

        self.box.valueChanged.connect(self._from_box)
        self.slider.valueChanged.connect(self._from_slider)

        layout = QHBoxLayout(self)
        layout.addWidget(self.box)
        layout.addWidget(self.slider)

    def _from_slider(self, v):
        self.box.blockSignals(True)
        self.box.setValue(v / 10)
        self.box.blockSignals(False)
        self.changed.emit()

    def _from_box(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(int(round(v * 10)))
        self.slider.blockSignals(False)
        self.changed.emit()
