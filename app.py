import sys
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets
from enum import Enum
from serializer import Serializer
from threading import Thread
from time import sleep


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


to_send = False


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent, QtCore.Qt.Window)
        self.edit = QLineEdit("Write command here")
        self.preview = QLabel("PREVIEW")
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.button = QPushButton("Send Data")
        self.dropdown = QtWidgets.QComboBox(self)
        self.fill_dropdown()
        self.fill_layout()
        self.button.clicked.connect(self.send_data)
        self.setFixedSize(400, 200)

    def fill_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.dropdown)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        layout.addWidget(self.preview)

        self.setLayout(layout)

    def fill_dropdown(self):
        for code in Codes:
            self.dropdown.addItem(str(code.name).replace('_', ' '))

    def send_data(self):
        global to_send
        to_send = True


class Application(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        widget = CentralWidget()
        self.setCentralWidget(widget)


def run_gui():
    app = QApplication(sys.argv)
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())



def run_serializer():
    global to_send
    serializer = Serializer()
    while True:
        if to_send:
            serializer.to_send = to_send
            to_send = False


if __name__ == "__main__":
    t2 = Thread(target=run_serializer)
    t2.start()
    t1 = Thread(target=run_gui)
    t1.start()
