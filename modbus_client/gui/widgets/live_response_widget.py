from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class LiveResponseWidget(QGroupBox):

    def __init__(self):
        super(LiveResponseWidget, self).__init__()
        self.setAlignment(Qt.AlignCenter)
