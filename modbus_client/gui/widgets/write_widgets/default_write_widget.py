import csv

from modbus_client.gui.style.custom_elements import *


class DefaultWWidget(QWidget):
    address_constraint = (0, 65535)
    data_constraint = (0, 65535)
    data_list = list()
    csv_imported = False

    def __init__(self):
        super(DefaultWWidget, self).__init__()
        self.layout = QFormLayout()
        self.firstAddress = ClickableLineEdit('0')

    def import_csv(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open data csv', '/home')
        with open(file_name[0]) as input_csv:
            self.data_list = list()
            reader = csv.reader(input_csv)
            for row in reader:
                self.data_list.extend(row)

        if len(self.data_list) > 0:
            self.csv_imported = True
