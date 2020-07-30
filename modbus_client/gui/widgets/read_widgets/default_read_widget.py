from modbus_client.gui.style.custom_elements import *


class DefaultRWidget(QWidget):
    address_constraint = (0, 65535)
    unit_address_constraint = (1, 65535)

    def __init__(self):
        super(DefaultRWidget, self).__init__()
        self.layout = QFormLayout()
        self.unitAddress = ClickableLineEdit('1')
        self.unitAddress.setToolTip('Unit address.\nValue between 1 and 65535')
        self.address = ClickableLineEdit('0')
        self.count = ClickableLineEdit('1')
        self.layout.addRow("Unit address: ", self.unitAddress)

    def validate_input(self, window):
        try:
            unit_address = int(self.unitAddress.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect unit address input type.')
            return False

        if not (self.unit_address_constraint[0] <= unit_address <= self.unit_address_constraint[1]):
            ErrorDialog(window, f'Unit address out of bounds.\n'
                                f'Has to be between {self.unit_address_constraint[0]} and '
                                f'{self.unit_address_constraint[1]}')

        try:
            curr_address = int(self.address.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect address input type. Must be integer.')
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f'First address out of bounds.\n'
                        f'Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}')
            return False

        try:
            curr_count = int(self.count.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect count input type. Must be integer.')
            return False

        if not (self.count_constraint[0] <= curr_count <= self.count_constraint[1]):
            ErrorDialog(window,
                        f'Count out of bounds.\n'
                        f'Has to be between {self.count_constraint[0]} and {self.count_constraint[1]}')
            return False

        return True

    def generate_message(self, transaction_id, function_code):

        return {'transaction_id': transaction_id,
                'unit_address': int(self.unitAddress.text()),
                'function_code': function_code,
                'address': int(self.address.text()),
                'count': int(self.count.text())}
