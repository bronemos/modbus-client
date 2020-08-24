from datetime import datetime

from PySide2 import QtGui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate
from modbus_client.resources.codes import ErrorCodes


class ResponseLogWidget(QGroupBox):

    def __init__(self):
        super(ResponseLogWidget, self).__init__('RESPONSE LOG')
        self.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setItemDelegate(CenterDelegate())
        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def update_log(self, transaction: dict):
        self.table.setSortingEnabled(False)
        self.table.insertRow(0)
        timestamp = QTableWidgetItem(datetime.now().strftime('%H:%M:%S'))
        self.table.setItem(0, 0, timestamp)
        transaction_id = QTableWidgetItem()
        transaction_id.setData(Qt.EditRole, transaction['transaction_id'])
        self.table.setItem(0, 1, transaction_id)
        unit_address = QTableWidgetItem()
        unit_address.setData(Qt.EditRole, transaction['unit_address'])
        self.table.setItem(0, 2, unit_address)
        function_code = QTableWidgetItem()
        function_code.setData(Qt.EditRole, transaction['function_code'])
        self.table.setItem(0, 3, function_code)
        raw_response = QTableWidgetItem(str(transaction.get('raw_data', '-')))
        self.table.setItem(0, 4, raw_response)
        if transaction['function_code'] in [x.value for x in ErrorCodes]:
            error_color = QtGui.QColor(255, 114, 111)
            timestamp.setBackground(error_color)
            transaction_id.setBackground(error_color)
            unit_address.setBackground(error_color)
            function_code.setBackground(error_color)
            raw_response.setBackground(error_color)
        self.table.setSortingEnabled(True)


