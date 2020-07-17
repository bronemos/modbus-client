import PySide2

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2 import QtGui


class ClickableLineEdit(QLineEdit):
    focused = Signal()

    def __init__(self, default_value):
        super(ClickableLineEdit, self).__init__(default_value)
        self.default_value = default_value

    def focusInEvent(self, arg__1: PySide2.QtGui.QFocusEvent):
        super(ClickableLineEdit, self).focusInEvent(arg__1)
        self.focused.emit()


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class Switch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "1" if self.isChecked() else "0"
        bg_color = QtGui.QColor(119, 188, 31) if self.isChecked() else QtGui.QColor(240, 0, 0)

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(182, 182, 182))

        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        pen.setWidth(1.8)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2 * width, 2 * radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2 * radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)


class ErrorDialog(QDialog):

    def __init__(self, parent, error_message):
        super(ErrorDialog, self).__init__(parent)
        self.setWindowTitle("Input error!")
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.close)
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel(error_message))
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)
        self.exec_()