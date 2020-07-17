from modbus_client.gui.widgets.read_widgets.default_read_widget import DefaultRWidget
from modbus_client.gui.style.custom_elements import ErrorDialog


class ReadCoilsWidget(DefaultRWidget):

    def __init__(self):
        super(ReadCoilsWidget, self).__init__()
        self.count_constraint = (1, 2000)
        self.firstAddress.setToolTip(
            f"Address of the first coil.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.count.setToolTip(
            f"Number of coils to be read.\nValue between {self.count_constraint[0]} and {self.count_constraint[1]}.")
        self.layout.addRow("First coil address: ", self.firstAddress)
        self.layout.addRow("Coil count: ", self.count)
        self.setLayout(self.layout)
