from PySide2.QtWidgets import QPushButton

from modbus_client.gui.style.custom_elements import ErrorDialog
from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.resources.codes import Codes


class WriteMultipleCoilsWidget(DefaultWWidget):

    def __init__(self):
        super(WriteMultipleCoilsWidget, self).__init__()
        self.firstAddress.setToolTip(f'Addres of the first coil.\n'
                                     f'Value between {self.address_constraint[0]} and {self.address_constraint[1]}')

        self.importButton = QPushButton('Import CSV')
        self.importButton.clicked.connect(self.import_csv)

        self.layout.addRow('First coil address:', self.firstAddress)
        self.layout.addRow(self.importButton)
        self.setLayout(self.layout)

    def validate_input(self, window):
        if not self.validate_unit_address(window):
            return False
        try:
            curr_address = int(self.firstAddress.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect address input type. Must be integer.')
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f'Coil address out of bounds.\n'
                        f'Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}')
            return False

        try:
            for x in self.data_list:
                if x not in ('0', '1'):
                    ErrorDialog(window, 'Invalid data type detected in CSV.\n'
                                        'All values must be either 0 or 1.')
                    return False
        except ValueError:
            ErrorDialog(window, 'Invalid data type detected in CSV.\n'
                                'All data types must be integers.')
            return False

        if not self.csv_imported:
            ErrorDialog(window, 'CSV file empty or not imported.')
            return False

        return True

    def generate_message(self):
        return {'unit_address': int(self.unitAddress.text()),
                'address': int(self.firstAddress.text()),
                'data': self.data_list,
                'function_code': Codes.WRITE_MULTIPLE_COILS.value}
