from PySide6 import QtWidgets
from PySide6 import QtCore
from hindu import get_cord

import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure

import numpy as np
from hindu_calculation import *


class Plots3DResults(QtWidgets.QMainWindow):
    window_closed = QtCore.Signal()

    def __init__(self, modal_response, floor, time, modes, fp):
        super().__init__()
        self.floor = floor
        self.modal_response = modal_response
        self.time = time
        self.modes = modes
        self.walking_f = fp

        self.setWindowTitle("3D plots by grid")
        width = 600
        height = 435
        self.setFixedSize(width, height)

        file_tab = self.menuBar().addMenu("&File")
        file_tab.addAction("&Exit", self.close)

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
        self.acc_button.clicked.connect(self._max_acceleration_button)
        buttons_layout.addWidget(self.acc_button)

        self.vel_button = QtWidgets.QPushButton("Velocity")
        self.vel_button.setFixedSize(100, 35)
        self.vel_button.clicked.connect(self._max_velocity_button)
        buttons_layout.addWidget(self.vel_button)

        self.disp_button = QtWidgets.QPushButton("Displacement")
        self.disp_button.setFixedSize(100, 35)
        self.disp_button.clicked.connect(self._max_displacement_button)
        buttons_layout.addWidget(self.disp_button)

        self.accRMS_button = QtWidgets.QPushButton("Acceleration RMS")
        self.accRMS_button.setFixedSize(100, 35)
        self.accRMS_button.clicked.connect(self._max_acceleration_rms_button)
        buttons_layout.addWidget(self.accRMS_button)

        self.velRMS_button = QtWidgets.QPushButton("Velocity RMS")
        self.velRMS_button.setFixedSize(100, 35)
        self.velRMS_button.clicked.connect(self._max_velocity_rms_button)
        buttons_layout.addWidget(self.velRMS_button)

        response_type_buttons.setLayout(buttons_layout)

        self.empty_canvas_layout = QtWidgets.QGroupBox(self)
        self.empty_canvas_layout.setFixedSize(465, 315)
        self.empty_canvas_layout.move(5, 105)

        self.canvas_screen = QtWidgets.QVBoxLayout()

        self.canvas = FigureCanvasQTAgg(Figure())
        self.canvas_screen.addWidget(self.canvas)

        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def max_acceleration_at_point(self, x, y, modes, total, do_rms):
        self.response_type = "Z [m/s^2]"
        self.receiver = x, y
        self.resp = Acceleration(self.modal_response.acceleration_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))
        max_acc = 0
        max_rms = 0
        if do_rms:
            rms = MovingAverage1s(self.modal_response.acceleration_harm, self.time,
                                  self.floor.mode_scale(self.modes, self.receiver))
            max_rms = np.max(rms.moving_average)

        if modes and not total:
            max_acc = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif modes and total:
            max_acc = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif not modes and total:
            max_acc = np.max(np.abs(self.resp.total_response))

        if do_rms:
            return max_acc, max_rms
        else:
            return max_acc

    def max_velocity_at_point(self, x, y, modes, total, do_rms):
        self.response_type = "Z [m/s]"
        self.receiver = x, y
        self.resp = Velocity(self.modal_response.velocity_modes,
                             self.floor.mode_scale(self.modes, self.receiver))

        max_rms = 0
        max_vel = 0
        if do_rms:
            rms = MovingAverage1s(self.modal_response.velocity_harm, self.time,
                                  self.floor.mode_scale(self.modes, self.receiver))
            max_rms = np.max(rms.moving_average)

        if modes and not total:
            max_vel = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif modes and total:
            max_vel = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif not modes and total:
            max_vel = np.max(np.abs(self.resp.total_response))

        if do_rms:
            return max_vel, max_rms
        else:
            return max_vel

    def max_displacement_at_point(self, x, y, modes, total):
        self.response_type = "Z [m]"
        self.receiver = x, y
        self.resp = Displacement(self.modal_response.displacement_modes,
                                 self.floor.mode_scale(self.modes, self.receiver))

        max_disp = 0
        if modes and not total:
            max_disp = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif modes and total:
            max_disp = np.max(np.abs(self.resp.mode_response), axis=1).reshape(-1, 1)
        elif not modes and total:
            max_disp = np.max(np.abs(self.resp.total_response))

        return max_disp

    def _max_acceleration_button(self):
        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        x, y = get_cord()
        modes_checked = self.response_modes.isChecked()
        total_checked = self.response_total.isChecked()
        if total_checked and not modes_checked:
            max_accelerations = np.array(
                [self.max_acceleration_at_point(xi, yi, modes_checked, total_checked, False) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_total_response(x, y, max_accelerations, self.response_type, False, False)
        elif total_checked and modes_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_accelerations = []

            for xi, yi in zip(x_flat, y_flat):
                max_acc = self.max_acceleration_at_point(xi, yi, modes_checked, total_checked, False)
                max_accelerations.append(max_acc)
            # todo moze da se optimizuje, jer je total vec izracunat, samo da se izvuce
            total_acceleration = np.array(
                [self.max_acceleration_at_point(xi, yi, False, True, False) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_all_response(x, y, max_accelerations, self.modes, total_acceleration,
                                                 self.response_type)
        elif modes_checked and not total_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_accelerations = []

            for xi, yi in zip(x_flat, y_flat):
                max_acc = self.max_acceleration_at_point(xi, yi, modes_checked, total_checked, False)
                max_accelerations.append(max_acc)
            max_accelerations = np.array(max_accelerations)
            self.fig = plot_max_abs_mode_response(x, y, max_accelerations, self.modes, self.response_type)

        self.fig.suptitle('Maximum absolute acceleration')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _max_velocity_button(self):
        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        x, y = get_cord()
        modes_checked = self.response_modes.isChecked()
        total_checked = self.response_total.isChecked()
        if total_checked and not modes_checked:
            max_velocities = np.array(
                [self.max_velocity_at_point(xi, yi, modes_checked, total_checked, False) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_total_response(x, y, max_velocities, self.response_type, False, False)
        elif total_checked and modes_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_velocities = []
            for xi, yi in zip(x_flat, y_flat):
                max_vel = self.max_velocity_at_point(xi, yi, modes_checked, total_checked, False)
                max_velocities.append(max_vel)
            # todo moze da se optimizuje, jer je total vec izracunat, samo da se izvuce
            total_velocity = np.array(
                [self.max_velocity_at_point(xi, yi, False, True, False) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_all_response(x, y, max_velocities, self.modes, total_velocity, self.response_type)
        elif modes_checked and not total_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_velocities = []

            for xi, yi in zip(x_flat, y_flat):
                max_acc = self.max_velocity_at_point(xi, yi, modes_checked, total_checked, False)
                max_velocities.append(max_acc)

            max_velocities = np.array(max_velocities)
            self.fig = plot_max_abs_mode_response(x, y, max_velocities, self.modes, self.response_type)

        self.fig.suptitle('Maximum absolute velocity')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _max_displacement_button(self):

        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        x, y = get_cord()
        modes_checked = self.response_modes.isChecked()
        total_checked = self.response_total.isChecked()
        if total_checked and not modes_checked:
            max_velocities = np.array(
                [self.max_displacement_at_point(xi, yi, modes_checked, total_checked) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_total_response(x, y, max_velocities, self.response_type, False, False)
        elif total_checked and modes_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_displacements = []

            for xi, yi in zip(x_flat, y_flat):
                max_dis = self.max_displacement_at_point(xi, yi, modes_checked, total_checked)
                max_displacements.append(max_dis)
            # todo moze da se optimizuje, jer je total vec izracunat, samo da se izvuce
            total_displacement = np.array(
                [self.max_displacement_at_point(xi, yi, False, True) for xi, yi
                 in zip(x.flatten(), y.flatten())])
            self.fig = plot_max_abs_all_response(x, y, max_displacements, self.modes, total_displacement,
                                                 self.response_type)
        elif modes_checked and not total_checked:
            x_flat = x.flatten()
            y_flat = y.flatten()
            max_displacements = []
            for xi, yi in zip(x_flat, y_flat):
                max_dis = self.max_displacement_at_point(xi, yi, modes_checked, total_checked)
                max_displacements.append(max_dis)

            max_displacements = np.array(max_displacements)
            self.fig = plot_max_abs_mode_response(x, y, max_displacements, self.modes, self.response_type)

        self.fig.suptitle('Maximum absolute displacement')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _max_acceleration_rms_button(self):
        self.response_modes.setChecked(False)
        self.response_total.setChecked(True)
        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.response_type = 'Z (m/s^2)'
        x, y = get_cord()
        results = np.array([
            self.max_acceleration_at_point(xi, yi, False, True, True)
            for xi, yi in zip(x.flatten(), y.flatten())
        ])
        max_accelerations = results[:, 0]
        max_rms = results[:, 1]
        self.fig = plot_max_abs_total_response(x, y, max_accelerations, self.response_type, True, max_rms)
        self.fig.suptitle('Max Acceleration RMS')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)

    def _max_velocity_rms_button(self):
        self.response_modes.setChecked(False)
        self.response_total.setChecked(True)
        self.canvas_screen.removeWidget(self.canvas)
        self.canvas.deleteLater()
        self.response_type = 'Z (m/s)'
        x, y = get_cord()
        results = np.array([
            self.max_velocity_at_point(xi, yi, False, True, True)
            for xi, yi in zip(x.flatten(), y.flatten())
        ])
        max_velocities = results[:, 0]
        max_rms = results[:, 1]
        self.fig = plot_max_abs_total_response(x, y, max_velocities, self.response_type, True, max_rms)
        self.fig.suptitle('Max Velocity RMS')
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas_screen.addWidget(self.canvas)
        self.empty_canvas_layout.setLayout(self.canvas_screen)


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
        self.receiver_point_x.move(100, 5)
        receiver.addWidget(self.receiver_point_x)
        self.receiver_point_y = QtWidgets.QLineEdit(receiver_point_coordinates)
        self.receiver_point_y.setFixedSize(40, 25)
        receiver.addWidget(self.receiver_point_y)

        self.pick_button = QtWidgets.QPushButton("Pick point")
        self.pick_button.setFixedSize(100, 25)
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
            self.fig = plot_all_response(self.response_type, self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type, self.resp, self.time, self.modes)
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
            self.fig = plot_all_response(self.response_type, self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type, self.resp, self.time, self.modes)
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
            self.fig = plot_all_response(self.response_type, self.resp, self.time, self.modes)
        elif self.response_modes.isChecked() and self.response_total.isChecked() is False:
            self.fig = plot_mode_response(self.response_type, self.resp, self.time, self.modes)
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

        self.fig = plot_rms_response(self.response_type, self.resp, self.time, rms)  #plot_rms_response

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

        points.addWidget(QtWidgets.QLabel("Receiver point:    "), )
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
