from PySide2 import QtCore
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate


class HistorianWidget(QGroupBox):
    existing_responses = set()
    existing_requests = set()

    def __init__(self):
        super(HistorianWidget, self).__init__()
        layout = QHBoxLayout()

        request_box = QGroupBox("REQUEST HISTORY")
        request_box.setAlignment(QtCore.Qt.AlignCenter)
        self.request_history = QTableWidget()
        self.request_history.verticalHeader().hide()
        self.request_history.setItemDelegate(CenterDelegate())
        self.request_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.request_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.request_history.setColumnCount(len(header_labels))
        self.request_history.setHorizontalHeaderLabels(header_labels)
        req_layout = QVBoxLayout()
        req_layout.addWidget(self.request_history)
        request_box.setLayout(req_layout)

        response_box = QGroupBox("RESPONSE HISTORY")
        response_box.setAlignment(QtCore.Qt.AlignCenter)
        self.response_history = QTableWidget()
        self.response_history.verticalHeader().hide()
        self.response_history.setItemDelegate(CenterDelegate())
        self.response_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.response_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.response_history.setColumnCount(len(header_labels))
        self.response_history.setHorizontalHeaderLabels(header_labels)
        res_layout = QVBoxLayout()
        res_layout.addWidget(self.response_history)
        response_box.setLayout(res_layout)

        layout.addWidget(request_box)
        layout.addWidget(response_box)
        self.setLayout(layout)

    def load(self, cursor):
        cursor.execute('''SELECT * FROM response_history''')
        responses = cursor.fetchall()
        for response in responses:
            if response not in self.existing_responses:
                self.response_history.insertRow(0)
                self.response_history.setItem(0, 0, QTableWidgetItem(response[0]))
                self.response_history.setItem(0, 1, QTableWidgetItem(str(response[1])))
                self.response_history.setItem(0, 2, QTableWidgetItem(str(response[2])))
                self.response_history.setItem(0, 3, QTableWidgetItem(str(response[3])))
                self.response_history.setItem(0, 4, QTableWidgetItem(str(response[4])))

        self.existing_responses = self.existing_responses | set(responses)

        cursor.execute('''SELECT * FROM request_history''')
        requests = cursor.fetchall()
        for request in requests:
            if request not in self.existing_requests:
                self.request_history.insertRow(0)
                self.request_history.setItem(0, 0, QTableWidgetItem(request[0]))
                self.request_history.setItem(0, 1, QTableWidgetItem(str(request[1])))
                self.request_history.setItem(0, 2, QTableWidgetItem(str(request[2])))
                self.request_history.setItem(0, 3, QTableWidgetItem(str(request[3])))
                self.request_history.setItem(0, 4, QTableWidgetItem(str(request[4])))

        self.existing_requests = self.existing_requests | set(requests)
