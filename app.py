import sys
import traceback
import serializer
import asyncio

from threading import Thread
from style.widgets import *
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import *
from enum import Enum
from concurrent.futures import ThreadPoolExecutor


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


class Application(QMainWindow):
    threadpool = QThreadPool()
    executor = ThreadPoolExecutor(max_workers=1)
    connected = False

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.stackedMainWidget = QStackedWidget()

        self.mainWidget = QWidget()

        self.ConnectWidget = ConnectWidget()
        self.ConnectWidget.button.clicked.connect(self._connect_disconnect)

        self.ReadCoilsWidget = ReadCoilsWidget()

        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()

        self.DefaultWidget = DefaultWidget()

        self.stackedMainWidget.addWidget(self.DefaultWidget)
        self.stackedMainWidget.addWidget(self.ReadCoilsWidget)
        self.stackedMainWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedMainWidget.setEnabled(self.connected)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self.change_widget)
        form.addRow("Function: ", self.dropdown)
        layout.addWidget(self.ConnectWidget)
        layout.addLayout(form)
        layout.addWidget(self.stackedMainWidget)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

    def _connect_disconnect(self):
        if not self.connected:
            serializer_thread = Thread(target=serializer.start)
            check_connection_thread = Thread(
                target=lambda: asyncio.new_event_loop().run_until_complete(self.check_connection()))
            serializer_thread.start()
            check_connection_thread.start()
        else:
            serializer.req_queue.put("DC")
            self.connected = False
            self.stackedMainWidget.setEnabled(self.connected)
            self.ConnectWidget.button.setText("Connect")

    def change_widget(self):
        print("changing")
        current = str(self.dropdown.currentText())
        if current == "READ COILS":
            print("read coils")
            self.stackedMainWidget.setCurrentWidget(self.ReadCoilsWidget)
            self.dropdown.setCurrentText("READ COILS")
        elif current == "READ DISCRETE INPUTS":
            print("read discrete")
            self.stackedMainWidget.setCurrentWidget(self.ReadDiscreteInputsWidget)
            self.dropdown.setCurrentText("READ DISCRETE INPUTS")
        elif current == "READ HOLDING REGISTERS":
            self.stackedMainWidget.setCurrentWidget(self.ReadDiscreteInputsWidget)
            self.dropdown.setCurrentText("READ HOLDING REGISTERS")
            print("read holding")
        else:
            print("else")
            self.stackedMainWidget.setCurrentWidget(self.DefaultWidget)

    async def check_connection(self):
        ack = await asyncio.get_event_loop().run_in_executor(self.executor, self._wait_for_ack)
        if ack == "ACK":
            self.connected = True
            self.stackedMainWidget.setEnabled(self.connected)
            self.ConnectWidget.button.setText("Disconnect")

    def _wait_for_ack(self):
        try:
            message = serializer.res_queue.get()
            return message
        except Exception:
            return


def run_gui():
    app = QApplication()
    app.setStyle('Fusion')
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
