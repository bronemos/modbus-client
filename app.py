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


class Application(QMainWindow):
    executor = ThreadPoolExecutor(max_workers=1)

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.mainWidget = QStackedWidget()

        self.ConnectWidget = ConnectWidget()
        self.ConnectWidget.button.clicked.connect(self._connect)

        self.ReadCoilsWidget = ReadCoilsWidget()
        self.ReadCoilsWidget.dropdown.view().pressed.connect(self.change_widget)

        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()
        self.ReadDiscreteInputsWidget.dropdown.view().pressed.connect(self.change_widget)

        self.DefaultWidget = DefaultWidget()
        self.DefaultWidget.dropdown.view().pressed.connect(self.change_widget)

        self.mainWidget.addWidget(self.ConnectWidget)
        self.mainWidget.addWidget(self.DefaultWidget)
        self.mainWidget.addWidget(self.ReadCoilsWidget)
        self.mainWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.connect_buttons()

        self.setCentralWidget(self.mainWidget)

    def _connect(self):
        serialized_thread = Thread(target=serializer.start)
        check_connection_thread = Thread(target=asyncio.new_event_loop().run_until_complete(self.check_connection()))
        serialized_thread.start()
        check_connection_thread.start()

    def _dc(self):
        serializer.req_queue.put("DC")
        self.mainWidget.setCurrentWidget(self.ConnectWidget)

    def connect_buttons(self):
        i = 0
        while w := self.mainWidget.widget(i):
            try:
                w.DCButton.clicked.connect(self._dc)
            except AttributeError as e:
                print(e)
            finally:
                i += 1

    def change_widget(self):
        current = str(self.mainWidget.currentWidget().dropdown.currentText())
        if current == "READ COILS":
            print("read coils")
            self.mainWidget.setCurrentWidget(self.ReadCoilsWidget)
            self.mainWidget.currentWidget().dropdown.setCurrentText("READ COILS")
        elif current == "READ DISCRETE INPUTS":
            print("read discrete")
            self.mainWidget.setCurrentWidget(self.ReadDiscreteInputsWidget)
            self.mainWidget.currentWidget().dropdown.setCurrentText("READ DISCRETE INPUTS")
        elif current == "READ HOLDING REGISTERS":
            print("read holding")
        else:
            print("else")
            self.mainWidget.setCurrentWidget(self.DefaultWidget)

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
