from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.gui.style.custom_elements import Switch


class WriteSingleCoilWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleCoilWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the coil.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.switch = Switch()
        self.layout.addRow("Coil address: ", self.firstAddress)
        self.layout.addRow("Coil status: ", self.switch)
        self.setLayout(self.layout)

    def validate_input(self, window):
        pass