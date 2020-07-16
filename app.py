import sys
import serializer
import asyncio
import queue

from threading import Thread
from style.widgets import *
from PySide2.QtWidgets import *
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import *
from concurrent.futures import ThreadPoolExecutor

protocol_code = '0000'
unit_address = '01'


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
        self.ReadHoldingRegistersWidget = ReadHoldingRegistersWidget()
        self.ReadInputRegistersWidget = ReadInputRegistersWidget()
        self.WriteSingleCoilWidget = WriteSingleCoilWidget()
        self.WriteSingleRegisterWidget = WriteSingleRegisterWidget()
        self.WriteMultipleRegistersWidget = WriteMultipleRegistersWidget()

        self.stackedMainWidget.addWidget(self.ReadCoilsWidget)
        self.stackedMainWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedMainWidget.addWidget(self.ReadHoldingRegistersWidget)
        self.stackedMainWidget.addWidget(self.ReadInputRegistersWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleCoilWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleRegisterWidget)
        self.stackedMainWidget.addWidget(self.WriteMultipleRegistersWidget)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_widget)
        form.addRow("Function: ", self.dropdown)
        layout.addWidget(self.ConnectWidget)
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
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.connecting_movie)
            self.ConnectWidget.button.setText("Connecting...")
            self.ConnectWidget.button.setEnabled(False)
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
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.disconnected_movie)

    async def _check_connection(self):
        ack = await asyncio.get_event_loop().run_in_executor(self.executor, self._get_message)

        if ack == "ACK":
            self.connected = True
            self.ConnectWidget.button.setEnabled(True)
            self.reqWidget.setEnabled(self.connected)
            self.ConnectWidget.button.setText("Disconnect")
            self.ConnectWidget.indicator.setMovie(self.ConnectWidget.connected_movie)

    def _change_widget(self):
        current = self.dropdown.currentIndex()
        self.stackedMainWidget.setCurrentIndex(current)
        self.dropdown.setCurrentIndex(current)

    def _validate_and_send(self):
        validate_and_send_thread = Thread(target=self._validate_and_send_thread)
        validate_and_send_thread.start()

    def _validate_and_send_thread(self):
        current = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value

        # handling READ function validation and message assembly
        if 1 <= current <= 4:
            try:
                curr_address = int(self.stackedMainWidget.currentWidget().firstAddress.text())
            except ValueError:
                ErrorDialog(self, "Incorrect address input type. Must be integer.")
                return

            min_address = int(self.stackedMainWidget.currentWidget().address_constraint[0])
            max_address = int(self.stackedMainWidget.currentWidget().address_constraint[1])

            if not (min_address <= curr_address <= max_address):
                ErrorDialog(self, f"First address out of bounds.\nHas to be between {min_address} and {max_address}")
                return

            try:
                min_count = int(self.stackedMainWidget.currentWidget().count_constraint[0])
                max_count = int(self.stackedMainWidget.currentWidget().count_constraint[1])
                curr_count = int(self.stackedMainWidget.currentWidget().count.text())
            except ValueError:
                ErrorDialog(self, "Incorrect count input type, must be integer.")
                return

            if not (min_count <= curr_count <= max_count):
                ErrorDialog(self, f"Count out of bounds.\nHas to be between {min_count} and {max_count}")
                return

            first_address = int(self.stackedMainWidget.currentWidget().firstAddress.text())
            count = int(self.stackedMainWidget.currentWidget().count.text())
            function_code = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value
            message = {"message_id": self.last_id, "function_code": function_code, "first_address": first_address, "count": count}

        # handling write single coil validation and assembly
        elif current == 5:

            try:
                curr_address = int(self.stackedMainWidget.currentWidget().firstAddress.text())
            except ValueError:
                ErrorDialog(self, "Incorrect address input type. Must be integer.")
                return

            min_address = int(self.stackedMainWidget.currentWidget().address_constraint[0])
            max_address = int(self.stackedMainWidget.currentWidget().address_constraint[1])

            if not (min_address <= curr_address <= max_address):
                ErrorDialog(self, f"Coil address out of bounds.\nHas to be between {min_address} and {max_address}")
                return

            address_stripped = int(self.stackedMainWidget.currentWidget().firstAddress.text())
            status = self.stackedMainWidget.currentWidget().switch.isChecked()
            function_code = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value

            message = {"message_id": self.last_id, "first_address": address_stripped, "status": status, "function_code": function_code}

        elif current == 5:
            pass

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
    app.setApplicationDisplayName("Modbus Client GUI")
    app.setStyle('Fusion')
    mainWindow = Application()
    p = mainWindow.palette()
    p.setColor(mainWindow.backgroundRole(), Qt.white)
    mainWindow.setPalette(p)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()
