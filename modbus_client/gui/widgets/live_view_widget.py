from PySide2 import QtCore
from PySide2.QtWidgets import *


class LiveViewWidget(QGroupBox):

    def __init__(self):
        super(LiveViewWidget, self).__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)
