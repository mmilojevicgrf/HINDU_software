from PySide6 import QtWidgets


class TableWindow(QtWidgets.QWidget):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TableWindow, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, svs_num):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.svs_num = svs_num
            self.setWindowTitle('Insert modal masses')
            layout = QtWidgets.QVBoxLayout()
            layout_title = QtWidgets.QLabel("Insert modal masses")
            layout.addWidget(layout_title)

            self.table_widget = QtWidgets.QTableWidget()
            self.table_widget.setRowCount(self.svs_num)
            self.table_widget.setColumnCount(1)
            self.table_widget.setHorizontalHeaderLabels(['Modal mass [kg]'])
            self.setGeometry(610, 375, 150, 300)

            self.modal_masses = [0.0] * self.svs_num

            for row in range(self.svs_num):
                item = QtWidgets.QTableWidgetItem("0.0")
                self.table_widget.setItem(row, 0, item)

            self.table_widget.itemChanged.connect(self.update_modal_masses)
            layout.addWidget(self.table_widget)

            save_button = QtWidgets.QPushButton("Save", self)
            save_button.setFixedSize(100, 50)
            save_button.clicked.connect(self.save_and_exit)
            layout.addWidget(save_button)

            self.setLayout(layout)

            self.initialized = True

    def update_modal_masses(self, item):
        row = item.row()
        value = item.text().strip()
        # print(f"Item changed in row {row}: '{value}'")
        try:
            float_value = float(value)
            self.modal_masses[row] = float_value
            #print(f"Updated modal mass at row {row}: {self.modal_masses[row]}")
        except ValueError:
            self.modal_masses[row] = 0.0
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
        # print("Current modal_masses list:", self.modal_masses)  # Debug print

    def save_and_exit(self):
        self.close()

    def closeEvent(self, event):
        # print("Modal masses before exiting:", self.modal_masses)
        event.accept()

    def get_modal_masses(self):
        return self.modal_masses
