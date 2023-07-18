from PySide6 import QtWidgets
from PySide6 import QtCore

import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure

import numpy as np
from hindu_calculation import *


class TimeDomainResults(QtWidgets.QMainWindow):

    window_closed = QtCore.Signal()

    def __init__(self, modal_response, floor, time, modes, fp):
        super().__init__()

        self.floor = floor
        self.modal_response = modal_response
        self.time = time
        self.modes = modes
        self.walking_f = fp

        self.setWindowTitle("Time domain response diagrams")
        width = 600
        height = 435
        self.setFixedSize(width, height)

        file_tab = self.menuBar().addMenu("&File")
        file_tab.addAction("&Exit", self.close)

        receiver_point_coordinates = QtWidgets.QGroupBox("Receiver point", self)
        receiver_point_coordinates.setFixedSize(300, 70)
        receiver_point_coordinates.move(5, 30)

        receiver = QtWidgets.QHBoxLayout(self)
        receiver.addWidget(QtWidgets.QLabel("Coordinates:"))

        self.receiver_point_x = QtWidgets.QLineEdit(receiver_point_coordinates)
        self.receiver_point_x.setFixedSize(40, 25)
        self.receiver_point_x.move(100,5)
        receiver.addWidget(self.receiver_point_x)
        self.receiver_point_y = QtWidgets.QLineEdit(receiver_point_coordinates)
        self.receiver_point_y.setFixedSize(40, 25)
        receiver.addWidget(self.receiver_point_y)

        self.pick_button = QtWidgets.QPushButton("Pick point")
        self.pick_button.setFixedSize(100,25)
        self.pick_button.clicked.connect(self._pick_point)
        receiver.addWidget(self.pick_button)

        receiver_point_coordinates.setLayout(receiver)

        check_box_modes = QtWidgets.QGroupBox("Response", self)
        check_box_modes.setFixedSize(285, 70)
        check_box_modes.move(310, 30)

        checkbox_layout = QtWidgets.QVBoxLayout()

        self.response_modes = QtWidgets.QCheckBox("Response by modes")
        self.response_modes.setChecked(False)
        checkbox_layout.addWidget(self.response_modes)

        self.response_total = QtWidgets.QCheckBox("Superimposed response")
        self.response_total.setChecked(True)
        checkbox_layout.addWidget(self.response_total)

        check_box_modes.setLayout(checkbox_layout)

        response_type_buttons = QtWidgets.QGroupBox(self)
        response_type_buttons.setFixedSize(120, 315)
        response_type_buttons.move(475, 105)

        buttons_layout = QtWidgets.QVBoxLayout()

        self.acc_button = QtWidgets.QPushButton("Acceleration")
        self.acc_button.setFixedSize(100, 35)
        self.acc_button.clicked.connect(self._acceleration_button)
        buttons_layout.addWidget(self.acc_button)

        self.vel_button = QtWidgets.QPushButton("Velocity")
        self.vel_button.setFixedSize(100, 35)
        self.vel_button.clicked.connect(self._velocity_button)
        buttons_layout.addWidget(self.vel_button)

        self.disp_button = QtWidgets.QPushButton("Displacement")
        self.disp_button.setFixedSize(100, 35)
        self.disp_button.clicked.connect(self._displacement_button)
        buttons_layout.addWidget(self.disp_button)

        self.accRMS_button = QtWidgets.QPushButton("Acceleration RMS")
        self.accRMS_button.setFixedSize(100, 35)
        self.accRMS_button.clicked.connect(self._acceleration_rms_button)
        buttons_layout.addWidget(self.accRMS_button)

        self.velRMS_button = QtWidgets.QPushButton("Velocity RMS")
        self.velRMS_button.setFixedSize(100, 35)
        self.velRMS_button.clicked.connect(self._velocity_rms_button)
        buttons_layout.addWidget(self.velRMS_button)

        response_type_buttons.setLayout(buttons_layout)

        self.empty_canvas_layout = QtWidgets.QGroupBox(self)
        self.empty_canvas_layout.setFixedSize(465, 315)
        self.empty_canvas_layout.move(5, 105)

        self.canvas_screen = QtWidgets.QVBoxLayout()

        self.canvas = FigureCanvasQTAgg(Figure())
        self.canvas_screen.addWidget(self.canvas)

        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _acceleration_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.response_type = "Acceleration [m/s^2]"
        self.resp = Acceleration(self.modal_response.acceleration_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))

        if self.response_modes.isChecked() and self.response_total.isChecked():
            self.fig = plot_all_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() is False and self.response_total.isChecked():
            self.fig = plot_total_response(self.response_type, self.resp, self.time)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _velocity_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.response_type = "Velocity [m/s]"
        self.resp = Velocity(self.modal_response.velocity_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))

        if self.response_modes.isChecked() and self.response_total.isChecked():
            self.fig = plot_all_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() is False and self.response_total.isChecked():
            self.fig = plot_total_response(self.response_type, self.resp, self.time)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _displacement_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.response_type = "Displacement [m]"
        self.resp = Displacement(self.modal_response.displacement_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))

        if self.response_modes.isChecked() and self.response_total.isChecked():
            self.fig = plot_all_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type,self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() is False and self.response_total.isChecked():
            self.fig = plot_total_response(self.response_type, self.resp, self.time)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _acceleration_rms_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()

        self.response_type = "Acceleration [m/s^2]"
        self.resp = Acceleration(self.modal_response.acceleration_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))
        rms = MovingAverage1s(self.modal_response.acceleration_harm, self.time,
                              self.floor.mode_scale(self.modes, self.receiver))

        self.fig = plot_rms_response(self.response_type, self.resp, self.time, rms)#plot_rms_response

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

        self.response_modes.setChecked(False)
        self.response_total.setChecked(True)

    def _velocity_rms_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()

        self.response_type = "Velocity [m/s]"
        self.resp = Velocity(self.modal_response.velocity_modes,
                             self.floor.mode_scale(self.modes, self.receiver))
        rms = MovingAverage1step(self.resp.total_response, self.time, self.walking_f)

        self.fig = plot_rms_response(self.response_type, self.resp, self.time, rms)  # plot_rms_response

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

        self.response_modes.setChecked(False)
        self.response_total.setChecked(True)

    def _pick_point(self):
        self.point = PickPoint(self.floor)
        self.point.show()
        self.point.window_closed.connect(self._input_receiver)
        self.point.window_closed.connect(self._receiver)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def _input_receiver(self):

        receiver = self.point.receiver
        self.receiver_point_x.setText(str(receiver[0]))
        self.receiver_point_y.setText(str(receiver[1]))

    def _receiver(self):
        self.receiver = ([float(self.receiver_point_x.text()), float(self.receiver_point_y.text())])


class PickPoint(QtWidgets.QWidget):

    window_closed = QtCore.Signal()

    def __init__(self, floor):
        super().__init__()
        self.floor = floor
        self.setWindowTitle("Receiver point")
        width = 700
        height = 550
        self.setFixedSize(width, height)

        point_coordinates = QtWidgets.QGroupBox("Selected point", self)
        point_coordinates.setFixedSize(690, 80)
        point_coordinates.move(5, 5)

        points = QtWidgets.QHBoxLayout(self)

        points.addWidget(QtWidgets.QLabel("Receiver point:    "),)
        self.receiver_point_lcd_x = QtWidgets.QLCDNumber()

        self.receiver_point_lcd_x.setFixedSize(70, 40)
        points.addWidget(self.receiver_point_lcd_x)
        self.receiver_point_lcd_y = QtWidgets.QLCDNumber()
        self.receiver_point_lcd_y.setFixedSize(70, 40)
        points.addWidget(self.receiver_point_lcd_y)

        ok_button = QtWidgets.QPushButton("Ok", self)
        ok_button.setFixedSize(70, 40)

        points.addWidget(ok_button)
        ok_button.clicked.connect(self.close)

        reset_button = QtWidgets.QPushButton("Reset", self)
        reset_button.setFixedSize(70, 40)
        reset_button.clicked.connect(self._reset_button)
        points.addWidget(reset_button)

        point_coordinates.setLayout(points)

        floor_layout = QtWidgets.QGroupBox("Pick a point", self)
        floor_layout.setFixedSize(690, 450)
        floor_layout.move(5, 100)

        self.floor_grid = QtWidgets.QGridLayout(self)
        self._floor_layout()
        floor_layout.setLayout(self.floor_grid)

        self.click = 0

        plt.connect('button_press_event', self._on_click)

    def _floor_layout(self):

        self.fig, self.a = self.floor.geometry()
        self.plot = FigureCanvasQTAgg(self.fig)
        self.floor_grid.addWidget(self.plot)

    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()

    def _on_click(self, event):

        event.button = MouseButton.LEFT

        global ix, iy
        try:

            ix, iy = round(event.xdata, 1), round(event.ydata, 1)
            if self.click == 0:
                self.receiver = np.array([ix, iy])
                self.receiver_point_lcd_x.display(ix)
                self.receiver_point_lcd_y.display(iy)
                self.a.scatter(ix, iy, s=5)
                self.plot.draw()
            self.click += 1

        except Exception:
            pass

    def _reset_button(self):

        self.floor_grid.removeWidget(self.plot)
        self.plot.deleteLater()
        self._floor_layout()
        self.receiver_point_lcd_x.display(0.0)
        self.receiver_point_lcd_y.display(0.0)

        self.click = 0
        plt.connect('button_press_event', self._on_click)

