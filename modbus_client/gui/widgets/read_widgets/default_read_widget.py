from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets.default_widget import DefaultWidget


class DefaultRWidget(DefaultWidget):
    address_constraint = (0, 65535)

    def __init__(self):
        super(DefaultRWidget, self).__init__()
        self.address = ClickableLineEdit("0")
        self.count = ClickableLineEdit("1")
        self.count.focused.connect(lambda: self.clear_line(self.count))
        self.address.focused.connect(lambda: self.clear_line(self.address))

    def validate_input(self, window):

        try:
            curr_address = int(self.address.text())
        except ValueError:
            ErrorDialog(window, "Incorrect address input type. Must be integer.")
            return False

        if not (self.address_constraint[0] <= curr_address <= self.address_constraint[1]):
            ErrorDialog(window,
                        f"First address out of bounds.\n"
                        f"Has to be between {self.address_constraint[0]} and {self.address_constraint[1]}")
            return False

        try:
            curr_count = int(self.count.text())
        except ValueError:
            ErrorDialog(window, "Incorrect count type, must be integer.")
            return False

        if not (self.count_constraint[0] <= curr_count <= self.count_constraint[1]):
            ErrorDialog(window,
                        f"Count out of bounds.\n"
                        f"Has to be between {self.count_constraint[0]} and {self.count_constraint[1]}")
            return False

        return True

    def generate_message(self, message_id, function_code):

        return {'message_id': message_id,
                'function_code': function_code,
                'address': int(self.address.text()),
                'count': int(self.count.text())}
