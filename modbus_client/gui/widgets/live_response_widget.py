from PySide2.QtWidgets import *


class LiveResponseWidget(QWidget):

    def __init__(self):
        super(LiveResponseWidget, self).__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        layout.addWidget(self.table)


        self.setLayout(layout)
