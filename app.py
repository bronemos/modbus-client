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
    threadpool = QThreadPool()
    executor = ThreadPoolExecutor(max_workers=1)
    connected = False
    last_id = 0

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.stackedMainWidget = QStackedWidget()

        self.mainWidget = QWidget()

        self.ConnectWidget = ConnectWidget()
        self.ConnectWidget.button.clicked.connect(self._connect_disconnect)

        self.ReadCoilsWidget = ReadCoilsWidget()

        self.ReadDiscreteInputsWidget = ReadDiscreteInputsWidget()

        self.DefaultWidget = DefaultWidget()

        self.stackedMainWidget.addWidget(self.ReadCoilsWidget)
        self.stackedMainWidget.addWidget(self.ReadDiscreteInputsWidget)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_widget)
        form.addRow("Function: ", self.dropdown)
        layout.addWidget(self.ConnectWidget)
        movie = QtGui.QMovie("dot-splash.gif")
        # indicator = QLabel()
        # indicator.setMovie(movie)
        # movie.start()
        # layout.addWidget(indicator)
        req_label = QLabel("REQUEST")
        req_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(req_label)
        layout.addWidget(QHLine())

        form.addRow(self.stackedMainWidget)

        self.sendButton = QPushButton("SEND")
        self.sendButton.clicked.connect(self._validate_and_send)
        form.addRow(self.sendButton)

        self.reqWidget = QWidget()
        self.reqWidget.setEnabled(self.connected)

        self.reqWidget.setLayout(form)

        layout.addWidget(self.reqWidget)

        res_label = QLabel("RESPONSE")
        self.res_message = QLabel()
        self.res_message.setAlignment(Qt.AlignCenter)
        res_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(res_label)
        layout.addWidget(QHLine())
        layout.addWidget(self.res_message)

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

    def _connect_disconnect(self):
        if not self.connected:
            serializer_thread = Thread(target=serializer.start)
            check_connection_thread = Thread(
                target=lambda: asyncio.new_event_loop().run_until_complete(self._check_connection()))
            serializer_thread.start()
            check_connection_thread.start()
        else:
            serializer.req_queue.put("DC")
            self.connected = False
            self.reqWidget.setEnabled(self.connected)
            self.ConnectWidget.button.setText("Connect")

    async def _check_connection(self):
        ack = await asyncio.get_event_loop().run_in_executor(self.executor, self._get_message)

        if ack == "ACK":
            self.connected = True
            self.reqWidget.setEnabled(self.connected)
            self.ConnectWidget.button.setText("Disconnect")

    def _change_widget(self):
        print("changing")
        current = str(self.dropdown.currentText())
        if current == "READ COILS":
            self.stackedMainWidget.setCurrentWidget(self.ReadCoilsWidget)
            self.dropdown.setCurrentText("READ COILS")
        elif current == "READ DISCRETE INPUTS":
            self.stackedMainWidget.setCurrentWidget(self.ReadDiscreteInputsWidget)
            self.dropdown.setCurrentText("READ DISCRETE INPUTS")
        elif current == "READ HOLDING REGISTERS":
            self.stackedMainWidget.setCurrentWidget(self.ReadDiscreteInputsWidget)
            self.dropdown.setCurrentText("READ HOLDING REGISTERS")
        else:
            self.stackedMainWidget.setCurrentWidget(self.DefaultWidget)

    def _validate_and_send(self):
        hex_id_stripped = str(hex(self.last_id))[2:]
        first_address_stripped = str(hex(int(self.stackedMainWidget.currentWidget().firstAddress.text())))[2:]
        count_stripped = str(hex(int(self.stackedMainWidget.currentWidget().count.text())))[2:]
        message = '0' * (4 - len(hex_id_stripped)) + hex_id_stripped + protocol_code + '0006' + unit_address + getattr(
            Codes, self.dropdown.currentText().replace(' ', '_')).value + '0' * (
                          4 - len(first_address_stripped)) + first_address_stripped + '0' * (
                          4 - len(count_stripped)) + count_stripped
        print(message)
        self.last_id += 1
        serializer.req_queue.put(message)
        asyncio.new_event_loop().run_until_complete(self.show_response())

    async def show_response(self):
        message = await asyncio.get_event_loop().run_in_executor(self.executor, self._get_message)
        current_selection = self.dropdown.currentText()
        if current_selection == "READ COILS":
            self.res_message.setText("Coils set are: " + str(message))
        elif current_selection == "READ DISCRETE INPUTS":
            self.res_message.setText("")
        elif current_selection == "READ HOLDING REGISTERS":
            self.res_message.setText("")
        elif current_selection == "READ INPUT REGISTERS":
            self.res_message.setText("")

    def _get_message(self):
        try:
            message = serializer.res_queue.get()
            return message
        except queue.Empty:
            return


def run_gui():
    app = QApplication()
    app.setStyle('Fusion')
    mainWindow = Application()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
