import PySide2

from PySide2.QtCore import Signal
from PySide2.QtWidgets import *


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
