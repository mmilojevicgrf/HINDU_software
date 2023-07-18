from PySide6 import QtGui
from PySide6.QtGui import QAction
from menu_floor_tab import *
from results_tab import *
import numpy as np

window_height = 500
window_width = 800


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("Hindu")
        self.setWindowIcon(QtGui.QIcon("picture4.jpg"))
        self.setFixedSize(window_width, window_height)

        self.main_layout = QtWidgets.QGridLayout()
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)

        self._create_menu()
        self._mode_selection_section()
        self._input_parameters_section()
        self._walking_path_section()
        self._create_empty_canvas()

    def _load_geometry_and_modes_window(self):

        self.load_geometry_modes_tab = LoadGeometryModes()

        self.load_geometry_modes_tab.window_closed.connect(self._mode_checklist)
        self.load_geometry_modes_tab.window_closed.connect(self._input_files)
        self.load_geometry_modes_tab.window_closed.connect(self._input_floor)
        self.load_geometry_modes_tab.window_closed.connect(self._plot_canvas)
        self.load_geometry_modes_tab.window_closed.connect(self._active_edit_button)
        self.load_geometry_modes_tab.window_closed.connect(self._active_force_tab)

        self.load_geometry_modes_tab.show()

    def _define_walking_path_window(self):

        self.load_walking_path_tab = WalkingPath(self.floor)
        self.load_walking_path_tab.window_closed.connect(self._input_path)
        self.load_walking_path_tab.show()

    def _time_domain_results_window(self):

        self.time_domain_response = TimeDomainResults(self.response, self.floor, self.time_vector, self.modes,
                                                      self.walking_frequency)
        self.time_domain_response.show()

    def _input_files(self):
        self.dat_file = self.load_geometry_modes_tab.dat
        self.rpts = self.load_geometry_modes_tab.rpts

    def _create_menu(self):
        file_tab = self.menuBar().addMenu("&File")
        file_tab.addAction("&Exit", self.close)

        floor_tab = self.menuBar().addMenu("&Floor")
        self.floor_tab_option = QAction("&Load geometry/modes", self)
        self.floor_tab_option.triggered.connect(self._load_geometry_and_modes_window)
        floor_tab.addAction(self.floor_tab_option)

        self.walking_path_option = QAction("&Define walking path", self)
        self.walking_path_option.triggered.connect(self._define_walking_path_window)
        floor_tab.addAction(self.walking_path_option)
        self.walking_path_option.setDisabled(True)

        self.force_tab = self.menuBar().addMenu("&Force model")
        self.force_tab.setDisabled(True)

        self.kerr_force = QAction("Kerr", self)
        self.kerr_force.setCheckable(True)

        self.force_tab.addAction(self.kerr_force)

        self.rainer_force = QAction("Rainer", self)
        self.rainer_force.setCheckable(True)
        self.force_tab.addAction(self.rainer_force)

        self.zivanovic_force = QAction("Živanović", self)
        self.zivanovic_force.setCheckable(True)
        self.force_tab.addAction(self.zivanovic_force)

        self.arup_force = QAction("Arup", self)
        self.arup_force.setCheckable(True)
        self.force_tab.addAction(self.arup_force)

        self.results_tab = self.menuBar().addMenu("&Response diagrams")
        self.results_tab.setDisabled(True)

        self.time_domain_tab = QAction("&Time domain", self)
        self.time_domain_tab.triggered.connect(self._time_domain_results_window)
        self.results_tab.addAction(self.time_domain_tab)

        self.options_tab = self.menuBar().addMenu("&Options")
        self.options_tab.setDisabled(True)

        self.help_tab = self.menuBar().addMenu("&Help")
        self.help_tab.setDisabled(True)

        self.force_tab.triggered.connect(self._pick_force)

    def _mode_checklist(self):

        self.start_note.deleteLater()
        self.list_widget = QtWidgets.QListWidget()
        for mode in range(np.size(self.load_geometry_modes_tab.rpts)):
            line = QtWidgets.QListWidgetItem("Mode  "+str(mode+1))
            self.list_widget.addItem(line)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        scroll_bar = QtWidgets.QScrollBar(self)
        self.list_widget.setVerticalScrollBar(scroll_bar)
        self.ms_layout.addWidget(self.list_widget)

        select_all = QtWidgets.QCheckBox("Select all modes", self.available_modes)
        select_all.toggled.connect(self._select_all)

        self.list_widget.itemSelectionChanged.connect(self._selection_of_modes)

        self.ms_layout.addWidget(select_all)

    def _selection_of_modes(self):
        self.modes = [i for i, _ in enumerate(self.rpts)]

    def _select_all(self):
        self.list_widget.selectAll()

    def _mode_selection_section(self):

        self.available_modes = QtWidgets.QGroupBox("Available modes")
        self.available_modes.setFixedSize(225, 150)
        self.ms_layout = QtWidgets.QFormLayout()
        self.available_modes.setLayout(self.ms_layout)

        self.start_note = QtWidgets.QLabel("Modal characteristics \n are not loaded yet", self.available_modes)

        self.ms_layout.addWidget(self.start_note)

        self.main_layout.addWidget(self.available_modes, 0, 0)

    def _input_parameters_section(self):

        box = QtWidgets.QGroupBox("Input Parameters")
        box.setFixedSize(225, 160)
        ip_layout = QtWidgets.QFormLayout()
        box.setLayout(ip_layout)

        self.input_weight = QtWidgets.QLineEdit(box)
        ip_layout.addRow("Pedestrian Weight [N]:", self.input_weight)

        self.input_step = QtWidgets.QLineEdit(box)
        ip_layout.addRow("Step Length [m]:", self.input_step)

        self.input_time = QtWidgets.QLineEdit(box)
        ip_layout.addRow("Time Increment [s]:", self.input_time)

        self.input_frequency = QtWidgets.QLineEdit(box)
        ip_layout.addRow("Walking Frequency [Hz]:", self.input_frequency)

        self.input_damp = QtWidgets.QLineEdit(box)
        ip_layout.addRow("Damping ratio [%]:", self.input_damp)

        self.main_layout.addWidget(box, 1, 0)

    def _walking_path_section(self):

        box = QtWidgets.QGroupBox("Walking Path")
        box.setFixedSize(225, 150)

        wp_layout = QtWidgets.QGridLayout()
        box.setLayout(wp_layout)

        self.start_point_x = QtWidgets.QLineEdit(box)
        self.start_point_y = QtWidgets.QLineEdit(box)

        self.end_point_x = QtWidgets.QLineEdit(box)
        self.end_point_y = QtWidgets.QLineEdit(box)

        wp_layout.addWidget(QtWidgets.QLabel("Coordinates: "), 0, 0)
        wp_layout.addWidget(QtWidgets.QLabel("           X"), 0, 1)
        wp_layout.addWidget(QtWidgets.QLabel("           Y"), 0, 2)

        wp_layout.addWidget(QtWidgets.QLabel("Start point"), 1, 0)
        wp_layout.addWidget(QtWidgets.QLabel("End point"), 2, 0)

        wp_layout.addWidget(self.start_point_x, 1, 1)
        wp_layout.addWidget(self.start_point_y, 1, 2)

        wp_layout.addWidget(self.end_point_x, 2, 1)
        wp_layout.addWidget(self.end_point_y, 2, 2)

        buttons = QtWidgets.QHBoxLayout()
        self.edit_button = QtWidgets.QPushButton("Edit points")
        self.edit_button.setFixedSize(100, 30)
        self.edit_button.setDisabled(True)
        self.edit_button.clicked.connect(self._define_walking_path_window)

        self.calculate_button = QtWidgets.QPushButton("Calculate")
        self.calculate_button.setFixedSize(100, 30)
        self.calculate_button.setDisabled(True)
        self.calculate_button.clicked.connect(self._calculate)
        self.calculate_button.clicked.connect(self._delete_mode_shapes_canvas)

        buttons.setSpacing(80)
        buttons.addWidget(self.edit_button)
        buttons.addWidget(self.calculate_button)

        wp_layout.addLayout(buttons, 4, 0, 1, 2)

        self.main_layout.addWidget(box, 2, 0)

    def _create_empty_canvas(self):

        self.empty_canvas_layout = QtWidgets.QVBoxLayout()

        self.canvas = FigureCanvasQTAgg(Figure())
        self.empty_canvas_layout.addWidget(self.canvas)

        self.main_layout.addLayout(self.empty_canvas_layout, 0, 1, 3, 3)

    def _input_floor(self):
        self.floor = Floor(self.dat_file, self.rpts)
        self.walking_path_option.setDisabled(False)
        self.mode = 0

    def _plot_canvas(self):

        self.canvas_layout = QtWidgets.QVBoxLayout()

        self._text_canvas()
        self._mode_shape_canvas()
        self._buttons_canvas()

        self.main_layout.addLayout(self.canvas_layout, 0, 1, 3, 3)
        self.setLayout(self.main_layout)


    def _mode_plus_one(self):
        widget = QtWidgets.QWidget()
        while self.text_layout.count():
            item = self.text_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.main_layout.removeItem(self.text_layout)
        self.main_layout.removeWidget(self.plot)
        if self.mode == len(self.floor.frequency)-1:
            self.mode = 0
        else:
            self.mode = self.mode + 1
        self._plot_canvas()

    def _mode_minus_one(self):
        widget = QtWidgets.QWidget()
        while self.text_layout.count():
            item = self.text_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.main_layout.removeItem(self.text_layout)
        self.main_layout.removeWidget(self.plot)
        if self.mode == 0:
            self.mode = len(self.floor.frequency)-1
        else:
            self.mode = self.mode - 1
        self._plot_canvas()

    def _buttons_canvas(self):

        button_layout = QtWidgets.QHBoxLayout()
        button_back = QtWidgets.QPushButton("Previous mode")
        button_back.setFixedSize(150, 50)

        button_next = QtWidgets.QPushButton("Next mode")
        button_next.setFixedSize(150, 50)

        button_layout.addWidget(button_back)
        button_layout.addWidget(button_next)

        self.canvas_layout.addLayout(button_layout)

        button_back.clicked.connect(self._mode_minus_one)
        button_next.clicked.connect(self._mode_plus_one)

    def _mode_shape_canvas(self):
        self.fig = self.floor.plot(self.mode)
        self.plot = FigureCanvasQTAgg(self.fig)
        self.canvas_layout.addWidget(self.plot)

    def _text_canvas(self):
        self.text_layout = QtWidgets.QVBoxLayout()
        text1 = "Mode number:   " + str(self.mode + 1)
        text2 = "Frequency is:   " + str(self.floor.frequency[self.mode]) + "  Hz"
        text3 = "Modal mass is:   " + str(self.floor.modal_mass[self.mode]) + "  kg"
        self.text_layout.addWidget(QtWidgets.QLabel(text1))
        self.text_layout.addWidget(QtWidgets.QLabel(text2))
        self.text_layout.addWidget(QtWidgets.QLabel(text3))
        self.canvas_layout.addLayout(self.text_layout)

    def _input_path(self):

        start = self.load_walking_path_tab.start
        self.start_point_x.setText(str(start[0]))
        self.start_point_y.setText(str(start[1]))

        end = self.load_walking_path_tab.end
        self.end_point_x.setText(str(end[0]))
        self.end_point_y.setText(str(end[1]))

    def _active_edit_button(self):

        self.edit_button.setDisabled(False)

    def _active_force_tab(self):
        self.force_tab.setDisabled(False)

    def _data_entry(self):

        if self.input_weight.text() == '':
            self.input_weight.setStyleSheet("QLineEdit"
                                            "{"
                                            "background : red;"
                                            "}")
        else:
            self.input_weight.setStyleSheet("QLineEdit"
                                            "{"
                                            "background : white;"
                                            "}")
            self.weight = float(self.input_weight.text())

        if self.input_step.text() == '':
            self.input_step.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : red;"
                                          "}")
        else:
            self.input_step.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : white;"
                                          "}")
            self.step = float(self.input_step.text())

        if self.input_time.text() == '':
            self.input_time.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : red;"
                                          "}")
        else:
            self.input_time.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : white;"
                                          "}")
            self.increment = float(self.input_time.text())

        if self.input_frequency.text() == '':
            self.input_frequency.setStyleSheet("QLineEdit"
                                               "{"
                                               "background : red;"
                                               "}")
        else:
            self.input_frequency.setStyleSheet("QLineEdit"
                                               "{"
                                               "background : white;"
                                               "}")
            self.walking_frequency = float(self.input_frequency.text())

        if self.input_damp.text() == '':
            self.input_damp.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : red;"
                                          "}")
        else:
            self.input_damp.setStyleSheet("QLineEdit"
                                          "{"
                                          "background : white;"
                                          "}")
            self.damping = float(self.input_damp.text())/100

        self.path_start = ([float(self.start_point_x.text()), float(self.start_point_y.text())])
        self.path_end = ([float(self.end_point_x.text()), float(self.end_point_y.text())])

    def _pick_force(self, action):

        if action.isChecked():
            self.force_input = action.text()
            self.calculate_button.setDisabled(False)
            [action.setChecked(False) for action in self.force_tab.actions() if action.text() != self.force_input]
        else:
            self.calculate_button.setDisabled(True)

    def _calculate(self):

        self._data_entry()

        self.response, self.time_vector = calculation(self.floor, self.force_input, self.damping, self.path_start,
                                                      self.path_end, self.modes, self.walking_frequency, self.weight,
                                                      self.step, self.increment)
        self.results_tab.setDisabled(False)

    def _delete_mode_shapes_canvas(self):
        self.main_layout.removeItem(self.canvas_layout)
        self.delete_canvas = QtWidgets.QVBoxLayout()
        self.delete_plot = FigureCanvasQTAgg(Figure())
        self.delete_canvas.addWidget(self.delete_plot)
        self.main_layout.addLayout(self.delete_canvas, 0, 1, 3, 3)
