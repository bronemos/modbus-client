import serializer
import asyncio
import queue

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2 import QtCore, QtWidgets
from enum import Enum
from style.custom_elements import *
from concurrent.futures import ThreadPoolExecutor

protocol_code = '0000'
unit_address = '01'


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


def clear_line(lineedit):
    if lineedit.text() == lineedit.default_value:
        lineedit.clear()


class ConnectWidget(QWidget):

    def __init__(self, parent=None):
        super(ConnectWidget, self).__init__(parent, QtCore.Qt.Window)
        self.button = QPushButton("Connect")
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)


class DefaultWidget(QWidget):
    executor = ThreadPoolExecutor()

    def __init__(self, parent=None):
        super(DefaultWidget, self).__init__(parent, QtCore.Qt.Window)
        self.sendButton = QPushButton("SEND")
        self.dropdown = QComboBox(self)
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.layout = QFormLayout()
        self.layout.addRow("Function: ", self.dropdown)
        self.setLayout(self.layout)


class DefaultRWWidget(DefaultWidget):
    last_id = 0

    def __init__(self):
        super(DefaultRWWidget, self).__init__()
        self.firstAddress = ClickableLineEdit("0")
        self.count = ClickableLineEdit("1")
        self.sendButton.clicked.connect(self.validate_and_send)
        self.count.clicked.connect(lambda: clear_line(self.count))
        self.firstAddress.clicked.connect(lambda: clear_line(self.firstAddress))

    def validate_and_send(self):
        hex_id_stripped = str(hex(self.last_id))[2:]
        first_address_stripped = str(hex(int(self.firstAddress.text())))[2:]
        count_stripped = str(hex(int(self.count.text())))[2:]
        message = '0' * (4 - len(hex_id_stripped)) + hex_id_stripped + protocol_code + '0006' + unit_address + getattr(
            Codes, self.dropdown.currentText().replace(' ', '_')).value + '0' * (
                          4 - len(first_address_stripped)) + first_address_stripped + '0' * (
                              4 - len(count_stripped)) + count_stripped
        print(message)
        serializer.req_queue.put(message)
        asyncio.get_event_loop().run_until_complete(self.show_response())

    async def show_response(self):
        message = await asyncio.get_event_loop().run_in_executor(self.executor, self.get_message)
        self.messageLabel = QLabel(str(message))
        self.layout.addWidget(self.messageLabel)
        self.setLayout(self.layout)

    def get_message(self):
        try:
            message = serializer.res_queue.get()
            return message
        except queue.Empty:
            return


class ReadCoilsWidget(DefaultRWWidget):

    def __init__(self):
        super(ReadCoilsWidget, self).__init__()
        self.layout.addRow("First coil address: ", self.firstAddress)
        self.layout.addRow("Coil count: ", self.count)
        self.layout.addWidget(self.sendButton)
        self.setLayout(self.layout)


class ReadDiscreteInputsWidget(DefaultRWWidget):
    def __init__(self):
        super(ReadDiscreteInputsWidget, self).__init__()
        self.layout.addRow("First input address: ", self.firstAddress)
        self.layout.addRow("Input count: ", self.count)
        self.layout.addWidget(self.sendButton)
        self.setLayout(self.layout)


class ReadHoldingRegistersWidget(DefaultRWWidget):
    def __init__(self):
        super(ReadHoldingRegistersWidget, self).__init__()
        self.layout.addRow("First input address: ", self.firstAddress)
        self.layout.addRow("Register count: ", self.count)
        self.layout.addWidget(self.sendButton)
        self.setLayout(self.layout)

