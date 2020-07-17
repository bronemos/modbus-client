from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget


class WriteMultipleRegistersWidget(DefaultWWidget):

    def __init__(self):
        super(WriteMultipleRegistersWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")

        self.layout.addRow("First register address: ", self.firstAddress)
        self.setLayout(self.layout)
