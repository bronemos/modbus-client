from modbus_client.gui.style.custom_elements import *
from modbus_client.gui.widgets.default_widget import DefaultWidget


class DefaultWWidget(DefaultWidget):
    address_constraint = (0, 65535)

    def __init__(self):
        super(DefaultWWidget, self).__init__()
        self.firstAddress = ClickableLineEdit("0")
        self.firstAddress.focused.connect(lambda: self.clear_line(self.firstAddress))
