from datetime import datetime

from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate


class RequestLogWidget(QGroupBox):

    def __init__(self):
        super(RequestLogWidget, self).__init__('REQUEST LOG')
        self.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()
        self.table.verticalHeader().hide()
        self.table.setItemDelegate(CenterDelegate())
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_log(self, transaction: dict):
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(datetime.now().strftime('%H:%M:%S')))
        self.table.setItem(0, 1, QTableWidgetItem(str(transaction.get('transaction_id', '-'))))
        self.table.setItem(0, 2, QTableWidgetItem(str(transaction.get('unit_address', '-'))))
        self.table.setItem(0, 3, QTableWidgetItem(str(transaction.get('function_code', '-'))))
        self.table.setItem(0, 4, QTableWidgetItem(str(transaction.get('raw_request', '-'))))

