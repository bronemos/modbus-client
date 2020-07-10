import style.custom_elements as guielements
import serializer
import asyncio
import queue

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2 import QtCore, QtWidgets
from enum import Enum
from concurrent.futures import ThreadPoolExecutor


class Codes(Enum):
    READ_COILS = '01'
    READ_DISCRETE_INPUTS = '02'
    READ_HOLDING_REGISTERS = '03'
    READ_INPUT_REGISTERS = '04'
    WRITE_SINGLE_COIL = '05'
    WRITE_SINGLE_REGISTER = '06'
    READ_EXCEPTION_STATUS = '07'
    DIAGNOSTICS = '08'
    WRITE_MULTIPLE_COILS = '0F'
    WRITE_MULTIPLE_REGISTERS = '10'


class DefaultWidget(QWidget):

    def __init__(self, parent=None):
        super(DefaultWidget, self).__init__(parent, QtCore.Qt.Window)
        self.DCButton = QPushButton("Disconnect")
        self.dropdown = QComboBox(self)
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        layout = QFormLayout()
        layout.addWidget(self.DCButton)
        layout.addRow("Function: ", self.dropdown)
        self.setLayout(layout)


class ConnectWidget(QWidget):

    def __init__(self, parent=None):
        super(ConnectWidget, self).__init__(parent, QtCore.Qt.Window)
        self.button = QPushButton("Connect")
        self.dropdown = QComboBox(self)
        self.dropdown.setEnabled(False)
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        layout = QFormLayout()
        layout.addWidget(self.button)
        layout.addRow("Function: ", self.dropdown)
        self.setLayout(layout)


class ReadCoilsWidget(QWidget):
    pass


class CentralWidget(QWidget):

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent, QtCore.Qt.Window)

        self.requestLabel = QLabel("REQUEST")
        self.requestLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.edit = guielements.ClickableLineEdit("abcd")
        self.edit.clicked.connect(self.clear_line)

        self.styleComboBox = QComboBox()

        self.preview = QLabel("PREVIEW")
        self.preview.setAlignment(QtCore.Qt.AlignCenter)

        self.button = QPushButton("Send Data")
        self.button.clicked.connect(self.change_layout)

        self.dropdown = QtWidgets.QComboBox(self)
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])

        self.separator = QFrame()
        self.separator.setGeometry(QRect(320, 150, 118, 3))
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.responseLabel = QLabel("RESPONSE")
        self.responseLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.messageLabel = QLabel()
        self.messageLabel.setAlignment(QtCore.Qt.AlignCenter)

        layout2 = QFormLayout()

        layout2.addRow("Function: ", self.dropdown)
        layout2.addWidget(self.button)

        self.layout = QFormLayout()

        self.layout.addWidget(self.requestLabel)
        self.layout.addRow("Function: ", self.dropdown)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.preview)
        self.layout.addWidget(self.separator)
        self.layout.addWidget(self.responseLabel)
        self.layout.addWidget(self.messageLabel)

        self.setLayout(self.layout)

    def validate_and_send(self):
        serializer.req_queue.put(self.edit.text())
        asyncio.get_event_loop().run_until_complete(self.put_message())

    def clear_line(self):
        if self.edit.text() == self.edit.default_value:
            self.edit.clear()
        else:
            self.edit.setText(self.edit.default_value)

    async def put_message(self):
        message = await asyncio.get_event_loop().run_in_executor(self.executor, self.get_message)
        self.messageLabel.setText(str(message))

    def get_message(self):
        try:
            message = serializer.res_queue.get()
            return message
        except queue.Empty:
            return

    def change_layout(self):
        self.setLayout(self.layout)
