from qtpy.QtCore import Signal
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton

class PlotCtrl(QWidget):
    gridToggle = Signal(bool)
    autoScaleToggle = Signal(bool)
    pauseToggle = Signal(bool)
    
    resetClicked = Signal()
    clearClicked = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(40)
        
        layout = QHBoxLayout(self)

        self._add_toggle(layout, "Сетка", self.gridToggle, checked=True)
        self._add_toggle(layout, "Автомасштаб", self.autoScaleToggle)
        self._add_toggle(layout, "Пауза", self.pauseToggle)

        self._add_button(layout, "Сброс вида", self.resetClicked)
        self._add_button(layout, "Очистить", self.clearClicked)

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
        