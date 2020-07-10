import sys
import traceback
import serializer
import asyncio

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

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.mainWidget = QStackedWidget()

        self.ConnectWidget = ConnectWidget()
        self.ConnectWidget.button.clicked.connect(self._connect)

        self.DefaultWidget = DefaultWidget()
        self.DefaultWidget.DCButton.clicked.connect(self._dc)

        self.mainWidget.addWidget(self.ConnectWidget)
        self.mainWidget.addWidget(self.DefaultWidget)

        self.setCentralWidget(self.mainWidget)

    def _connect(self):
        worker = Worker(serializer.start)
        self.threadpool.start(worker)
        asyncio.get_event_loop().run_until_complete(self.check_connection())

    def _dc(self):
        serializer.req_queue.put("DC")
        self.mainWidget.setCurrentWidget(self.ConnectWidget)

    async def check_connection(self):
        ack = await asyncio.get_event_loop().run_in_executor(self.executor, self.wait_for_ack)
        if ack == "ACK":
            self.mainWidget.setCurrentWidget(self.DefaultWidget)

    def wait_for_ack(self):
        try:
            message = serializer.res_queue.get()
            return message
        except Exception:
            return


def run_gui():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
