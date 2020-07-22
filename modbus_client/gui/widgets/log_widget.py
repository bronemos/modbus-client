from PySide2.QtCore import Qt
from PySide2.QtWidgets import *


class LogWidget(QGroupBox):

    def __init__(self, title):
        super(LogWidget, self).__init__(title)
        self.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ["Timestamp", "Transaction ID", "Unit Address", "Function Code", "Set List", "Register Data"]
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_log(self, response: dict):
        self.table.setRowCount(x := self.table.rowCount() + 1)

