from qtpy.QtCore import Signal
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFrame, QCheckBox

class PlotCtrl(QWidget):
    curveToggle = Signal(int, bool)
    gridToggle = Signal(bool)
    autoScaleToggle = Signal(bool)
    pauseToggle = Signal(bool)
    resetClicked = Signal()
    clearClicked = Signal()

    def __init__(self, names, colors):
        super().__init__()
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)

        self.curve_checks = []
        for i, (name, color) in enumerate(zip(names, colors)):
            cb = QCheckBox(name)
            cb.setChecked(True)
            cb.setStyleSheet(f"QCheckBox {{ color: {color}; font-weight: bold; }}")
            cb.toggled.connect(lambda checked, idx=i: self.curveToggled.emit(idx, checked))
            layout.addWidget(cb)
            self.curve_checks.append(cb)

        layout.addWidget(self._separator())

        self._add_toggle(layout, "Сетка", self.gridToggle, checked=True)
        self._add_toggle(layout, "Автомасштаб", self.autoScaleToggle)
        self._add_toggle(layout, "Пауза", self.pauseToggle)

        self._add_button(layout, "Сброс вида", self.resetClicked)
        self._add_button(layout, "Очистить", self.clearClicked)

        layout.addStretch()

    @staticmethod
    def _add_toggle(layout, text, signal, checked=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.toggled.connect(signal)
        layout.addWidget(btn)
        return btn

    @staticmethod
    def _add_button(layout, text, signal):
        btn = QPushButton(text)
        btn.clicked.connect(signal)
        layout.addWidget(btn)
        return btn

    @staticmethod
    def _separator():
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameStyle(QFrame.Sunken)
        return line

        