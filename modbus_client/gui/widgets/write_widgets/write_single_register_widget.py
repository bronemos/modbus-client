from modbus_client.gui.style.custom_elements import ClickableLineEdit
from modbus_client.gui.style.custom_elements import ErrorDialog
from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.resources.codes import Codes


class WriteSingleRegisterWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleRegisterWidget, self).__init__()
        self.firstAddress.setToolTip(
            f'Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.')
        self.registerData = ClickableLineEdit('0')

        # address and value constraints are the same
        self.registerData.setToolTip(
            f'Register data.\nValue between {self.data_constraint[0]} and {self.data_constraint[1]}')

        self.layout.addRow('Register address: ', self.firstAddress)
        self.layout.addRow('Register data: ', self.registerData)
        self.setLayout(self.layout)

    def validate_input(self, window):
        if not self.validate_unit_address(window):
            return False

        try:
            curr_address = int(self.firstAddress.text())

        except ValueError:
            ErrorDialog(window, 'Incorrect input type. Must be integer.')
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f'Register address out of bounds.\n'
                        f'Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}')
            return False
        try:
            curr_data = int(self.registerData.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect data input type. Muste be integer.')
            return False

        if not (self.data_constraint[0] <= curr_data <= self.data_constraint[1]):
            ErrorDialog(window,
                        f'Register data out of bounds.\n'
                        f'Has to be between {self.data_constraint[0]} and {self.data_constraint[1]}')
            return False

        return True

    def generate_message(self):
        return {'unit_address': int(self.unitAddress.text()),
                'address': int(self.firstAddress.text()),
                'data': int(self.registerData.text()),
                'function_code': Codes.WRITE_SINGLE_REGISTER.value}
