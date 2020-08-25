import csv
import os
from contextlib import suppress

from PySide2 import QtCore, QtGui
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import *

from modbus_client.gui.style.custom_elements import CenterDelegate
from modbus_client.resources.codes import ErrorCodes


class HistorianWidget(QGroupBox):

    def __init__(self):
        super(HistorianWidget, self).__init__()
        self.existing_responses = set()
        self.existing_requests = set()
        self.loaded = False

        layout = QHBoxLayout()

        request_box = QGroupBox('REQUEST HISTORY')
        request_box.setAlignment(QtCore.Qt.AlignCenter)
        self.export_request_history = QPushButton('Export to CSV')
        self.request_history = QTableView()
        self.request_rows = QStandardItemModel()
        self.request_history.setSortingEnabled(True)
        # self.request_history.verticalHeader().hide()
        self.request_history.setItemDelegate(CenterDelegate())
        # self.request_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.request_history.horizontalHeader().setStretchLastSection(True)
        self.request_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.request_header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.request_rows.setHorizontalHeaderLabels(self.request_header_labels)
        req_layout = QVBoxLayout()
        req_layout.addWidget(self.request_history)
        req_layout.addWidget(self.export_request_history)
        request_box.setLayout(req_layout)

        response_box = QGroupBox('RESPONSE HISTORY')
        response_box.setAlignment(QtCore.Qt.AlignCenter)
        self.export_response_history = QPushButton('Export to CSV')
        self.response_history = QTableView()
        self.response_rows = QStandardItemModel()
        self.response_history.setSortingEnabled(True)
        # self.response_history.verticalHeader().hide()
        self.response_history.setItemDelegate(CenterDelegate())
        # self.response_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.response_history.horizontalHeader().setStretchLastSection(True)
        self.response_history.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.response_header_labels = ['Timestamp', 'Transaction ID', 'Unit Address', 'Function Code', 'Data']
        self.response_rows.setHorizontalHeaderLabels(self.response_header_labels)
        res_layout = QVBoxLayout()
        res_layout.addWidget(self.response_history)
        res_layout.addWidget(self.export_response_history)
        response_box.setLayout(res_layout)

        layout.addWidget(request_box)
        layout.addWidget(response_box)
        self.setLayout(layout)

    def load(self, history):

        responses = history['response_history']

        self.response_history.setSortingEnabled(False)

        for response in responses:
            if response not in self.existing_responses:
                self.response_rows.insertRow(0)
                timestamp = QStandardItem()
                timestamp.setData(response[0], QtCore.Qt.EditRole)
                self.response_rows.setItem(0, 0, timestamp)
                transaction_id = QStandardItem()
                transaction_id.setData(response[1], QtCore.Qt.EditRole)
                self.response_rows.setItem(0, 1, transaction_id)
                unit_address = QStandardItem()
                unit_address.setData(response[2], QtCore.Qt.EditRole)
                self.response_rows.setItem(0, 2, unit_address)
                function_code = QStandardItem()
                function_code.setData(response[3], QtCore.Qt.EditRole)
                self.response_rows.setItem(0, 3, function_code)
                data = QStandardItem()
                data.setData(str(response[4]), QtCore.Qt.EditRole)
                self.response_rows.setItem(0, 4, data)
                if response[3] in [x.value for x in ErrorCodes]:
                    error_color = QtGui.QColor(255, 114, 111)
                    timestamp.setBackground(error_color)
                    transaction_id.setBackground(error_color)
                    unit_address.setBackground(error_color)
                    function_code.setBackground(error_color)
                    data.setBackground(error_color)

        self.response_history.setModel(self.response_rows)

        self.existing_responses = self.existing_responses | set(responses)
        self.response_history.setSortingEnabled(True)

        requests = history['request_history']
        self.request_history.setSortingEnabled(False)
        for request in requests:
            if request not in self.existing_requests:
                self.request_rows.insertRow(0)
                timestamp = QStandardItem()
                timestamp.setData(request[0], QtCore.Qt.EditRole)
                self.request_rows.setItem(0, 0, timestamp)
                transaction_id = QStandardItem()
                transaction_id.setData(request[1], QtCore.Qt.EditRole)
                self.request_rows.setItem(0, 1, transaction_id)
                unit_address = QStandardItem()
                unit_address.setData(request[2], QtCore.Qt.EditRole)
                self.request_rows.setItem(0, 2, unit_address)
                function_code = QStandardItem()
                function_code.setData(request[3], QtCore.Qt.EditRole)
                self.request_rows.setItem(0, 3, function_code)
                data = QStandardItem()
                data.setData(str(request[4]), QtCore.Qt.EditRole)
                self.request_rows.setItem(0, 4, data)
                if request[3] in [x.value for x in ErrorCodes]:
                    error_color = QtGui.QColor(255, 114, 111)
                    timestamp.setBackground(error_color)
                    transaction_id.setBackground(error_color)
                    unit_address.setBackground(error_color)
                    function_code.setBackground(error_color)
                    data.setBackground(error_color)

        self.request_history.setModel(self.request_rows)

        self.existing_requests = self.existing_requests | set(requests)
        self.request_history.setSortingEnabled(True)

    def export_request_history_to_csv(self, requests):
        with suppress(FileNotFoundError):
            path = os.path.abspath(__file__ + '/../')
            request_history_name = QFileDialog.getSaveFileName(self, 'Save file', path + '/request_history.csv',
                                                               'CSV (*.csv)',
                                                               options=QFileDialog.DontUseNativeDialog)
            request_history = open(request_history_name[0], 'w')
            with request_history:
                write = csv.writer(request_history)
                write.writerow(self.request_header_labels)
                write.writerows(requests)

    def export_response_history_to_csv(self, responses):
        with suppress(FileNotFoundError):
            path = os.path.abspath(__file__ + '/../')
            response_history_name = QFileDialog.getSaveFileName(self, 'Save file', path + '/response_history.csv',
                                                                'CSV (*.csv)',
                                                                options=QFileDialog.DontUseNativeDialog)
            response_history = open(response_history_name[0], 'w')
            with response_history:
                write = csv.writer(response_history)
                write.writerow(self.response_header_labels)
                write.writerows(responses)
