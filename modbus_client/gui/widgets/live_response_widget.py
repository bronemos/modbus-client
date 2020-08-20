from PySide2.QtCore import Qt
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate
from modbus_client.resources.codes import Codes


class LiveResponseWidget(QWidget):

    def __init__(self):
        super(LiveResponseWidget, self).__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().hide()
        self.table.setItemDelegate(CenterDelegate())
        #self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ['Address', 'Data']
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def refresh(self, message):
        self.table.setRowCount(0)
        self.table.setSortingEnabled(False)
        if message['function_code'] == Codes.READ_COILS.value or \
                message['function_code'] == Codes.READ_DISCRETE_INPUTS.value:
            for no, coil in enumerate(message['status_list'][:message['count']]):
                self.table.insertRow(curr := self.table.rowCount())
                address = QTableWidgetItem()
                address.setData(Qt.EditRole, no + message['address'])
                self.table.setItem(curr, 0, address)
                coil_state = QTableWidgetItem()
                coil_state.setData(Qt.EditRole, coil)
                self.table.setItem(curr, 1, coil_state)
        elif message['function_code'] == Codes.READ_HOLDING_REGISTERS.value or \
                message['function_code'] == Codes.READ_INPUT_REGISTERS.value:
            for no, data in enumerate(message['register_data']):
                self.table.insertRow(curr := self.table.rowCount())
                address = QTableWidgetItem()
                address.setData(Qt.EditRole, no + message['address'])
                self.table.setItem(curr, 0, address)
                table_data = QTableWidgetItem()
                table_data.setData(Qt.EditRole, data)
                self.table.setItem(curr, 1, table_data)
        self.table.setSortingEnabled(True)
