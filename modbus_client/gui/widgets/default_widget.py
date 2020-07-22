from concurrent.futures import ThreadPoolExecutor

from PySide2 import QtCore
from PySide2.QtWidgets import *


class DefaultWidget(QWidget):
    executor = ThreadPoolExecutor()

    def __init__(self, parent=None):
        super(DefaultWidget, self).__init__(parent, QtCore.Qt.Window)
        self.layout = QFormLayout()

    def clear_line(self, input_line):
        if input_line.text() == input_line.default_value:
            input_line.clear()
