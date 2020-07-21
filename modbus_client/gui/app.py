import asyncio
import queue
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from modbus_client.codes import Codes
from modbus_client.communication import serializer
from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets import *

protocol_code = '0000'


class Application(QMainWindow):
    executor = ThreadPoolExecutor(max_workers=1)
    connected = False
    message_id = 0

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
        self.WriteMultipleCoilsWidget = WriteMultipleCoilsWidget()

        self.stackedMainWidget.addWidget(self.ReadCoilsWidget)
        self.stackedMainWidget.addWidget(self.ReadDiscreteInputsWidget)
        self.stackedMainWidget.addWidget(self.ReadHoldingRegistersWidget)
        self.stackedMainWidget.addWidget(self.ReadInputRegistersWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleCoilWidget)
        self.stackedMainWidget.addWidget(self.WriteSingleRegisterWidget)
        self.stackedMainWidget.addWidget(self.WriteMultipleCoilsWidget)
        self.stackedMainWidget.addWidget(self.WriteMultipleRegistersWidget)

        layout = QVBoxLayout()
        form = QFormLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems([x.name.replace('_', ' ') for x in Codes])
        self.dropdown.activated[str].connect(self._change_widget)
        self.unitAddress = ClickableLineEdit('1')
        self.unitAddress.setToolTip("Unit address.\nValue between 1 and 65535")
        form.addRow("Unit address: ", self.unitAddress)
        form.addRow("Function: ", self.dropdown)
        layout.addWidget(self.ConnectWidget)
        req_label = QLabel("REQUEST")
        req_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(req_label)
        layout.addWidget(QHLine())

        form.addRow(self.stackedMainWidget)

        self.sendButton = QPushButton("SEND")
        self.sendButton.clicked.connect(self._validate_and_queue)
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

    def _validate_and_queue(self):
        try:
            unit_address = int(self.unitAddress.text())
        except ValueError:
            ErrorDialog(self, "Incorrect unit address value.")
            return

        if not self.stackedMainWidget.currentWidget().validate_input(self):
            return

        message = self.stackedMainWidget.currentWidget().generate_message(self.message_id, unit_address)

        print(message)
        self.message_id += 1
        serializer.req_queue.put(message)
        asyncio.new_event_loop().run_until_complete(self.show_response())

    async def show_response(self):
        message = await asyncio.get_event_loop().run_in_executor(self.executor, self._get_message)
        print(message)
        current_selection = getattr(Codes, self.dropdown.currentText().replace(' ', '_')).value
        if current_selection == 1:
            self.res_message.setText(f"Coils set are: {','.join(message['set_list'])}" if len(message['set_list'])
                                     else "No coils are set")
        elif current_selection == 2:
            self.res_message.setText(
                f"Discrete inputs status: {','.join(message['set_list'])}" if len(message['set_list'])
                else "No discrete inputs are set.")
        elif current_selection == 3:
            self.res_message.setText(f"Holding registers data: {','.join(message['register_data'])}")
        elif current_selection == 4:
            self.res_message.setText(f"Input registers data: {','.join(message['register_data'])}")

    def _get_message(self):
        try:
            message = serializer.res_queue.get()
            return message
        except queue.Empty:
            return


def run_gui():
    app = QApplication()
    app.setApplicationDisplayName('Modbus Client GUI')
    app.setStyle('Fusion')
    mainWindow = Application()
    p = mainWindow.palette()
    p.setColor(mainWindow.backgroundRole(), Qt.white)
    mainWindow.setPalette(p)
    mainWindow.show()
    sys.exit(app.exec_())
