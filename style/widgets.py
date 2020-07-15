from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2 import QtCore, QtWidgets
from enum import Enum
from style.custom_elements import *
from concurrent.futures import ThreadPoolExecutor

class Codes(Enum):
    READ_COILS = '01'
    READ_DISCRETE_INPUTS = '02'
    READ_HOLDING_REGISTERS = '03'
    READ_INPUT_REGISTERS = '04'
    WRITE_SINGLE_COIL = '05'
    WRITE_SINGLE_REGISTER = '06'
    WRITE_MULTIPLE_REGISTERS = '10'
    READ_EXCEPTION_STATUS = '07'
    DIAGNOSTICS = '08'
    WRITE_MULTIPLE_COILS = '0F'


def clear_line(lineedit):
    if lineedit.text() == lineedit.default_value:
        lineedit.clear()


class ConnectWidget(QWidget):

    def __init__(self, parent=None):
        super(ConnectWidget, self).__init__(parent, QtCore.Qt.Window)
        self.button = QPushButton("Connect")
        self.disconnected_movie = QtGui.QMovie("resources/disconnected.gif")
        self.connecting_movie = QtGui.QMovie("resources/connecting.gif")
        self.connected_movie = QtGui.QMovie("resources/connected.gif")
        self.disconnected_movie.setScaledSize(QSize(50, 50))
        self.connecting_movie.setScaledSize(QSize(50, 50))
        self.connected_movie.setScaledSize(QSize(50, 50))
        self.indicator = QLabel()
        self.indicator.setMovie(self.disconnected_movie)
        self.disconnected_movie.start()
        self.connected_movie.start()
        self.connecting_movie.start()

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.button)
        layout.addWidget(self.indicator)
        self.setLayout(layout)


class DefaultWidget(QWidget):
    executor = ThreadPoolExecutor()

    def __init__(self, parent=None):
        super(DefaultWidget, self).__init__(parent, QtCore.Qt.Window)
        self.layout = QFormLayout()
        self.setLayout(self.layout)


class DefaultRWidget(DefaultWidget):
    address_constraint = (0, 65535)

    def __init__(self):
        super(DefaultRWidget, self).__init__()
        self.firstAddress = ClickableLineEdit("0")
        self.count = ClickableLineEdit("1")
        self.count.focused.connect(lambda: clear_line(self.count))
        self.firstAddress.focused.connect(lambda: clear_line(self.firstAddress))


class DefaultWWidget(DefaultWidget):
    address_constraint = (0, 65535)

    def __init__(self):
        super(DefaultWWidget, self).__init__()
        self.firstAddress = ClickableLineEdit("0")
        self.firstAddress.focused.connect(lambda: clear_line(self.firstAddress))


class ReadCoilsWidget(DefaultRWidget):

    def __init__(self):
        super(ReadCoilsWidget, self).__init__()
        self.count_constraint = (1, 2000)
        self.firstAddress.setToolTip(
            f"Address of the first coil.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of coils to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}.")
        self.layout.addRow("First coil address: ", self.firstAddress)
        self.layout.addRow("Coil count: ", self.count)
        self.setLayout(self.layout)


class ReadDiscreteInputsWidget(DefaultRWidget):

    def __init__(self):
        super(ReadDiscreteInputsWidget, self).__init__()
        self.count_constraint = (1, 2000)
        self.firstAddress.setToolTip(
            f"Address of the first discrete input.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of discrete inputs to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}.")
        self.layout.addRow("First input address: ", self.firstAddress)
        self.layout.addRow("Input count: ", self.count)
        self.setLayout(self.layout)


class ReadHoldingRegistersWidget(DefaultRWidget):

    def __init__(self):
        super(ReadHoldingRegistersWidget, self).__init__()
        self.count_constraint = (1, 125)
        self.firstAddress.setToolTip(
            f"Address of the first holding register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of holding registers to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}.")
        self.layout.addRow("First input address: ", self.firstAddress)
        self.layout.addRow("Register count: ", self.count)
        self.setLayout(self.layout)


class ReadInputRegistersWidget(DefaultRWidget):

    def __init__(self):
        super(ReadInputRegistersWidget, self).__init__()
        self.count_constraint = (1, 125)
        self.firstAddress.setToolTip(
            f"Address of the first input register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of input registers to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}")
        self.layout.addRow("First input address: ", self.firstAddress)
        self.layout.addRow("Register count: ", self.count)
        self.setLayout(self.layout)


class WriteSingleCoilWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleCoilWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the coil.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.switch = Switch()
        self.layout.addRow("Coil address: ", self.firstAddress)
        self.layout.addRow("Coil status: ", self.switch)
        self.setLayout(self.layout)


class WriteSingleRegisterWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleRegisterWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.registerData = ClickableLineEdit("0")

        # address and value constraints are the same
        self.registerData.setToolTip(
            f"Register data.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}")

        self.layout.addRow("Register address: ", self.firstAddress)
        self.layout.addRow("Register data: ", self.registerData)
        self.setLayout(self.layout)


class WriteMultipleRegistersWidget(DefaultWWidget):

    def __init__(self):
        super(WriteMultipleRegistersWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")

        self.layout.addRow("First register address: ", self.firstAddress)
        self.setLayout(self.layout)
