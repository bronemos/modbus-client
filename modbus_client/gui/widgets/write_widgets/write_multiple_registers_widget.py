from PySide2.QtWidgets import QPushButton

from modbus_client.gui.style.custom_elements import ErrorDialog
from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.resources.codes import Codes


class WriteMultipleRegistersWidget(DefaultWWidget):

    def __init__(self):
        super(WriteMultipleRegistersWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")

        self.importButton = QPushButton("Import CSV")
        self.importButton.clicked.connect(self.import_csv)

        self.layout.addRow("First register address: ", self.firstAddress)
        self.layout.addRow(self.importButton)
        self.setLayout(self.layout)

    def validate_input(self, window):

        try:
            curr_address = int(self.firstAddress.text())
        except ValueError:
            ErrorDialog(window, "Incorrect address input type. Must be integer.")
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f"Register address out of bounds.\n"
                        f"Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}")
            return False

        try:
            self.data_list = [int(x) for x in self.data_list]
        except ValueError:
            ErrorDialog(window, "Invalid data type detected in CSV.\n"
                                "All data types must be integers.")
            return False

        if not self.csv_imported:
            ErrorDialog(window, "CSV file empty or not imported.")
            return False

        return True

    def generate_message(self, last_id, unit_address):
        return {'message_id': last_id,
                'unit_address': unit_address,
                'address': int(self.firstAddress.text()),
                'data': self.data_list,
                'function_code': Codes.WRITE_MULTIPLE_REGISTERS.value}
