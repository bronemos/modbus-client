from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate


class LiveResponseWidget(QWidget):

    def __init__(self):
        super(LiveResponseWidget, self).__init__()
        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.verticalHeader().hide()
        self.table.setItemDelegate(CenterDelegate())
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ['Address', 'Data']
        self.table.setColumnCount(len(header_labels))
        self.table.setHorizontalHeaderLabels(header_labels)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def refresh(self, message):
        self.table.setRowCount(0)
        if message['function_code'] == 1 or message['function_code'] == 2:
            for coil in message['set_list']:
                self.table.insertRow(0)
                self.table.setItem(0, 0, QTableWidgetItem(coil))
                self.table.setItem(0, 1, QTableWidgetItem(coil))
        elif message['function_code'] == 3 or message['function_code'] == 4:
            for data in message['register_data']:
                self.table.insertRow(0)
                self.table.setItem(0, 0, QTableWidgetItem(data))
                self.table.setItem(0, 1, QTableWidgetItem(data))
