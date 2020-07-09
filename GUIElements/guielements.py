import PySide2
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QLineEdit


class ClickableLineEdit(QLineEdit):
    clicked = Signal()

    def __init__(self, default_value):
        super(ClickableLineEdit, self).__init__()
        self.default_value = default_value
        self.setText(default_value)

    def mousePressEvent(self, arg__1: PySide2.QtGui.QMouseEvent):
        super(ClickableLineEdit, self).mousePressEvent(arg__1)
        self.clicked.emit()
