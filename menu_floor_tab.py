import os
import pandas as pd
from PySide6 import QtWidgets, QtCore
from hindu import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import MouseButton
import numpy as np


class LoadGeometryModes(QtWidgets.QWidget):

    window_closed = QtCore.Signal()
    # pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Load Geometry/Modes")
        width = 400
        height = 250
        self.setFixedSize(width, height)

        choose_software = QtWidgets.QGroupBox("Choose one of the listed software:", self)
        choose_software.setFixedSize(390, 240)
        choose_software.move(5, 5)

        save_button = QtWidgets.QPushButton("Save", self)
        save_button.setFixedSize(100, 50)
        save_button.move(290, 190)
        save_button.clicked.connect(self.close)

        self.layout = QtWidgets.QFormLayout()
        choose_software.setLayout(self.layout)

        self.software_list = QtWidgets.QComboBox(choose_software)
        self.layout.addRow(self.software_list)
        self.software_list.addItem("<Choose from software>")
        self.software_list.addItem("Abaqus CAE")
        self.software_list.addItem("Tower")
        self.software_list.addItem("SAP2000")

        self.software_list.activated.connect(self._browse_folder)
        self.software_list.activated.connect(self._get_data)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def _browse_folder(self):

        if self.software_list.currentText() == "<Choose from software>":
            return
        def_folder = os.path.expanduser("~")
        filters = "*.rpt *.dat"
        dialog = QtWidgets.QFileDialog.getOpenFileNames(self, "Select files to load:", def_folder, filter=filters)
        dialog_list = dialog[0]
        files_list = pd.Series(dialog_list)
        # Ovo je u stvari lista, nije putanja do foldera. Zadrzano je ime promenljive zbog poziva po ostalim metodama
        self.filepath = files_list
        # self.filepath = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))

    def _get_data(self):

        self.dat, self.rpts, self.dat_name = read_files(self.filepath)
        self._write()
        self.layout.addRow(self.report_dat)
        self.layout.addRow(self.rpt_num)

    def _write(self):
        self.report_dat = QtWidgets.QLabel("Loaded .dat file: " + self.dat_name)
        self.rpt_num = QtWidgets.QLabel("Number of loaded .rpt files: " + str(np.size(self.rpts)))


class WalkingPath(QtWidgets.QWidget):

    window_closed = QtCore.Signal()

    def __init__(self, floor):
        super().__init__()
        self.floor = floor
        self.setWindowTitle("Walking Path")
        width = 700
        height = 600
        self.setFixedSize(width, height)

        point_coordinates = QtWidgets.QGroupBox("Selected points", self)
        point_coordinates.setFixedSize(400, 110)
        point_coordinates.move(5, 5)

        points = QtWidgets.QGridLayout(self)

        points.addWidget(QtWidgets.QLabel("Start point:    "), 0, 0)
        self.start_point_lcd_x = QtWidgets.QLCDNumber()

        self.start_point_lcd_x.setFixedSize(70, 40)
        points.addWidget(self.start_point_lcd_x, 0, 1)
        self.start_point_lcd_y = QtWidgets.QLCDNumber()
        self.start_point_lcd_y.setFixedSize(70, 40)
        points.addWidget(self.start_point_lcd_y, 0, 2)

        points.addWidget(QtWidgets.QLabel("End point:    "), 1, 0)
        self.end_point_lcd_x = QtWidgets.QLCDNumber()
        self.end_point_lcd_x.setFixedSize(70, 40)
        points.addWidget(self.end_point_lcd_x, 1,  1)
        self.end_point_lcd_y = QtWidgets.QLCDNumber()
        self.end_point_lcd_y.setFixedSize(70, 40)
        points.addWidget(self.end_point_lcd_y, 1,  2)

        point_coordinates.setLayout(points)

        ok_button = QtWidgets.QPushButton("Ok", self)
        ok_button.setFixedSize(70, 40)
        ok_button.move(550, 20)
        ok_button.clicked.connect(self.close)

        reset_button = QtWidgets.QPushButton("Reset", self)
        reset_button.setFixedSize(70, 40)
        reset_button.move(550, 75)
        reset_button.clicked.connect(self._reset_button)

        self.floor_layout = QtWidgets.QGroupBox("Pick a point", self)
        self.floor_layout.setFixedSize(690, 450)
        self.floor_layout.move(5, 130)

        self.floor_grid = QtWidgets.QGridLayout(self)
        self._floor_layout()
        self.floor_layout.setLayout(self.floor_grid)

        self.click = 0

        plt.connect('button_press_event', self._on_click)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def _on_click(self, event):

        event.button = MouseButton.LEFT

        global ix, iy
        try:
            ix, iy = round(event.xdata, 1), round(event.ydata, 1)

            if self.click == 0:
                self.start_point_lcd_x.display(ix)
                self.start_point_lcd_y.display(iy)
                self.start = np.array([ix, iy])
                self.a.scatter(ix, iy, s=5)
                self.plot.draw()
            elif self.click == 1:
                self.end_point_lcd_x.display(ix)
                self.end_point_lcd_y.display(iy)
                self.end = np.array([ix, iy])
                self.a.scatter(ix, iy, s=5)
                self.plot.draw()
            self.click += 1

        except Exception:
            pass

    def _floor_layout(self):

        self.fig, self.a = self.floor.geometry()
        self.plot = FigureCanvasQTAgg(self.fig)
        self.floor_grid.addWidget(self.plot)

    def _reset_button(self):

        self.floor_grid.removeWidget(self.plot)
        self.plot.deleteLater()
        self._floor_layout()
        self.start_point_lcd_x.display(0.0)
        self.start_point_lcd_y.display(0.0)
        self.end_point_lcd_x.display(0.0)
        self.end_point_lcd_y.display(0.0)

        self.click = 0

        plt.connect('button_press_event', self._on_click)

