import sys
import traceback
import queue

from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import *
from enum import Enum
import serializer
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

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent, QtCore.Qt.Window)
        self.edit = QLineEdit("Write command here")
        self.preview = QLabel("PREVIEW")
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.button = QPushButton("Send Data")
        self.dropdown = QtWidgets.QComboBox(self)
        self.fill_dropdown()
        self.fill_layout()
        self.threadpool = QThreadPool()
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
        worker = Worker(serializer.start)
        self.threadpool.start(worker)


class Application(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        widget = CentralWidget()
        self.setCentralWidget(widget)


def run_gui():
    app = QApplication(sys.argv)
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
