from modbus_client.gui.style.custom_elements import ClickableLineEdit
from modbus_client.gui.widgets.write_widgets.default_write_widget import DefaultWWidget
from modbus_client.codes import Codes


class WriteSingleRegisterWidget(DefaultWWidget):

    def __init__(self):
        super(WriteSingleRegisterWidget, self).__init__()
        self.firstAddress.setToolTip(
            f"Address of the register.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}.")
        self.registerData = ClickableLineEdit("0")

        # address and value constraints are the same
        self.registerData.setToolTip(
            f"Register data.\nValue between {self.address_constraint[0]} and {self.address_constraint[1]}")

        self.layout.addRow("Register address: ", self.firstAddress)
        self.layout.addRow("Register data: ", self.registerData)
        self.setLayout(self.layout)

    def validate_input(self, window):
        return True

    def generate_message(self, last_id):
        return {"message_id": last_id,
                "address": int(self.firstAddress.text()),
                "data: ": int(self.registerData.text()),
                "function_code": Codes.WRITE_SINGLE_REGISTER.value}
