import sys
import traceback
import queue
import asyncio
import serializer
import style.guielements as guielements

from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import *
from enum import Enum
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


class Worker(QtCore.QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    def run(self):
        try:
            result = self.fn()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class WorkerSignals(QtCore.QObject):
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class CentralWidget(QWidget):
    threadpool = QThreadPool()
    worker = Worker(serializer.start)
    threadpool.start(worker)

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent, QtCore.Qt.Window)

        self.requestLabel = QLabel("REQUEST")
        self.requestLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.edit = guielements.ClickableLineEdit("abcd")

        self.styleComboBox = QComboBox()
        self.edit.clicked.connect(self.clear_line)

        self.preview = QLabel("PREVIEW")
        self.preview.setAlignment(QtCore.Qt.AlignCenter)

        self.button = QPushButton("Send Data")
        self.button.clicked.connect(self.send_data)

        self.dropdown = QtWidgets.QComboBox(self)
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])

        self.separator = QFrame()
        self.separator.setGeometry(QRect(320, 150, 118, 3))
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)

        self.responseLabel = QLabel("RESPONSE")
        self.responseLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.fill_layout()

    def fill_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(self.requestLabel)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        layout.addWidget(self.preview)
        layout.addWidget(self.separator)
        layout.addWidget(self.responseLabel)

        self.setLayout(layout)

    def send_data(self):
        serializer.to_send = True

    def clear_line(self):
        if self.edit.text() == self.edit.default_value:
            self.edit.clear()
        else:
            self.edit.setText(self.edit.default_value)


class Application(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        widget = CentralWidget()
        self.setCentralWidget(widget)


def run_gui():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
