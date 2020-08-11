import csv

from modbus_client.gui.style.custom_elements import *


class DefaultWWidget(QWidget):
    unit_address_constraint = (1, 255)
    address_constraint = (0, 65535)
    data_constraint = (0, 65535)
    data_list = list()
    csv_imported = False

    def __init__(self):
        super(DefaultWWidget, self).__init__()
        self.layout = QFormLayout()
        self.firstAddress = ClickableLineEdit('0')
        self.unitAddress = ClickableLineEdit('1')
        self.unitAddress.setToolTip(
            f'Unit address.\nValue between {self.unit_address_constraint[0]} and {self.unit_address_constraint[1]}')
        self.layout.addRow('Unit address: ', self.unitAddress)

    def import_csv(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open data csv', '/home')
        with open(file_name[0]) as input_csv:
            self.data_list = list()
            reader = csv.reader(input_csv)
            for row in reader:
                self.data_list.extend(row)

        if len(self.data_list) > 0:
            self.csv_imported = True

    def validate_unit_address(self, window):
        try:
            unit_address = int(self.unitAddress.text())
        except ValueError:
            ErrorDialog(window, 'Incorrect unit address input type.')
            return False

        if not (self.unit_address_constraint[0] <= unit_address <= self.unit_address_constraint[1]):
            ErrorDialog(window, f'Unit address out of bounds.\n'
                                f'Has to be between {self.unit_address_constraint[0]} and '
                                f'{self.unit_address_constraint[1]}')
            return False

        return True
