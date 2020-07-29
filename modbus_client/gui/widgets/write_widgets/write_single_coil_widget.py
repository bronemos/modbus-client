from modbus_client.gui.style.custom_elements import Switch, ErrorDialog
from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.resources.codes import Codes


class WriteSingleCoilWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleCoilWidget, self).__init__()
        self.firstAddress.setToolTip(
            f'Address of the coil.\n'
            f'Value between {self.address_constraint[0]} and {self.address_constraint[1]}.')
        self.switch = Switch()
        self.layout.addRow('Coil address: ', self.firstAddress)
        self.layout.addRow('Coil status: ', self.switch)
        self.setLayout(self.layout)

    def validate_input(self, window):

        try:
            curr_address = int(self.firstAddress.text())

        except ValueError:
            ErrorDialog(window, 'Incorrect input type. Must be integer.')
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f'Coil address out of bounds.\n'
                        f'Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}')
            return False

        return True

    def generate_message(self, last_id, unit_address):

        return {'transaction_id': last_id,
                'unit_address': unit_address,
                'address': int(self.firstAddress.text()),
                'status': self.switch.isChecked(),
                'function_code': Codes.WRITE_SINGLE_COIL.value}
