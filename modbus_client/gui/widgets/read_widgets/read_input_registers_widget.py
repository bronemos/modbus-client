from modbus_client.codes import Codes
from modbus_client.gui.widgets.read_widgets.default_read_widget import DefaultRWidget


class ReadInputRegistersWidget(DefaultRWidget):

    def __init__(self):
        super(ReadInputRegistersWidget, self).__init__()
        self.count_constraint = (1, 125)
        self.address.setToolTip(
            f"Address of the first input register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of input registers to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}")
        self.layout.addRow("First input address: ", self.address)
        self.layout.addRow("Register count: ", self.count)
        self.setLayout(self.layout)

    def generate_message(self, message_id):
        return super(ReadInputRegistersWidget, self).generate_message(message_id, Codes.READ_INPUT_REGISTERS.value)
