import math
from PySide6 import QtWidgets
from scipy.spatial import KDTree
from table_window import TableWindow
from scipy.interpolate import RegularGridInterpolator
from hindu_calculation import *

np.seterr(divide='ignore')
XCoord = None
YCoord = None


def get_cord():
    return globals()["Xcoord"], globals()["Ycoord"]


def read_experimental_files(filepath):
    uff_files_series = filepath[filepath.str.endswith(".uff")]
    uff_files = uff_files_series.tolist()
    svs_files_series = filepath[filepath.str.endswith(".svs")]
    svs_files = svs_files_series.tolist()
    return uff_files, svs_files


def read_files(filepath):
    rpt_files_series = filepath[filepath.str.endswith(".rpt")]
    rpt_files = rpt_files_series.tolist()
    dat_files_series = filepath[filepath.str.endswith(".dat")]
    dat_files = dat_files_series.tolist()
    if len(dat_files) > 1:
        print(f"More than one .dat file loaded! .dat files: {dat_files} ")
    dat_file = dat_files[0]
    return dat_file, rpt_files, str(dat_file)


def floor_geometry(NNode, rpt_file):
    rpt = open(rpt_file, "r")
    rpt_lines = rpt.read().splitlines()
    rpt.close()

    coordinates = np.zeros((NNode, 2))
    for node in range(NNode):
        line = ''.join(rpt_lines[16 + node]).split()
        coordinates[node, 0] = float(line[2])
        coordinates[node, 1] = float(line[3])

    globals()["Xcoord"] = coordinates[:, 0]
    globals()["Ycoord"] = coordinates[:, 1]

    return globals()["Xcoord"], globals()["Ycoord"]


def floor_geometry_experimental(NNode, uff_file):
    uff = open(uff_file, "r")
    uff_lines = uff.read().splitlines()
    uff.close()

    coordinates = np.zeros((NNode, 2))
    for node in range(NNode):
        line = ''.join(uff_lines[2 + node]).split()
        coordinates[node, 0] = float(line[4]) / 100
        coordinates[node, 1] = float(line[5]) / 100

    globals()["Xcoord"] = coordinates[:, 0]
    globals()["Ycoord"] = coordinates[:, 1]

    return globals()["Xcoord"], globals()["Ycoord"]


def modal_characteristics(dat_file, rpt_files):
    dat_file = open(dat_file, "r")
    rows = dat_file.read().splitlines()
    dat_file.close()

    row = [x for x in rows if 'NUMBER OF NODES DEFINED BY THE USER' in x]
    noderow = ' '.join(row).split()
    NNode = int(noderow[7])  # Broj cvorova mreze

    index = rows.index(' MODE NO      EIGENVALUE              FREQUENCY        '
                       ' GENERALIZED MASS   COMPOSITE MODAL DAMPING            ')

    NModes = len(rpt_files)

    m_shapes = np.zeros((NModes, NNode))

    mode = 0
    for mode_file in rpt_files:

        rpt = open(mode_file, "r")
        rpt_lines = rpt.read().splitlines()
        rpt.close()

        for node in range(NNode):
            line = ''.join(rpt_lines[16 + node]).split()
            m_shapes[mode][node] = float(line[7])
        mode = mode + 1

    freq = np.zeros(NModes)
    mmodal = np.zeros(NModes)

    for mode in range(NModes):
        row = ''.join(rows[index + 4 + mode]).split()

        freq[mode] = float(row[3])  # Frekvencije [Hz]
        mmodal[mode] = float(row[4])  # Modalne mase [kg]

    return NNode, freq, mmodal, m_shapes


def modal_characteristics_experimental(uff_files, svs_files):
    NModes = len(svs_files)
    svs_file = svs_files[0]
    with open(svs_file, 'r') as file:
        for num, line in enumerate(file, 1):
            if 'MODE SHAPE' in line:
                n_line_mode_shape = num + 1
            if 'END MODE DEFINITION' in line:
                n_line_end_mode_definition = num - 1
    NNode = int(n_line_end_mode_definition - n_line_mode_shape)
    m_shapes = np.zeros((NModes, NNode))
    normalized_m_shapes = np.zeros((NModes, NNode))
    mode = 0
    table_window = TableWindow(len(svs_files))
    mmodal_experimental = table_window.get_modal_masses()
    mmodal = np.zeros(NModes)
    freq = np.zeros(NModes)
    damp = np.zeros(NModes)
    for mode_file in svs_files:
        svs = open(mode_file, "r")
        svs_lines = svs.read().splitlines()
        svs.close()
        freq_line = ''.join(svs_lines[17]).split()
        damp_line = ''.join(svs_lines[20]).split()
        freq[mode] = float(freq_line[0])
        damp[mode] = float(damp_line[0])
        for node in range(NNode):
            line = ''.join(svs_lines[23 + node]).split()
            m_shapes[mode][node] = float(line[5])
        mode = mode + 1

    for mode in range(NModes):
        mmodal[mode] = mmodal_experimental[mode]
        max_val = np.max(m_shapes[mode])
        normalized_m_shapes[mode] = m_shapes[mode] / max_val

    return NNode, freq, mmodal, normalized_m_shapes, damp


class Floor:
    """Klasa Floor sadrzi sve geometrijske i materijalne karakteristike tavanice ucitane iz Abaqusa"""

    def __init__(self, uff_or_dat_file, svs_or_rpt_files, experimental):
        if experimental:
            self.NNode, self.frequency, self.modal_mass, self.m_shapes, self.damp = modal_characteristics_experimental(
                uff_or_dat_file, svs_or_rpt_files)
            self.x_coord, self.y_coord = floor_geometry_experimental(self.NNode, uff_or_dat_file[0])
        else:
            self.NNode, self.frequency, self.modal_mass, self.m_shapes = modal_characteristics(uff_or_dat_file,
                                                                                               svs_or_rpt_files)
            self.x_coord, self.y_coord = floor_geometry(self.NNode, svs_or_rpt_files[0])
        self.modal_stiffness = (2 * np.pi * self.frequency) ** 2 * self.modal_mass
        self.xy = np.column_stack((self.x_coord, self.y_coord))
        self.values = self.m_shapes
        self.use_regular_grid_interpolator = self._is_regular_grid()

        if not self.use_regular_grid_interpolator:
            self.kd_tree = KDTree(self.xy)

    def _is_regular_grid(self):
        unique_x = np.unique(self.x_coord)
        unique_y = np.unique(self.y_coord)
        return len(unique_x) == len(unique_y)

    def mode_shape_value(self, mode_number, point):
        values = self.values[mode_number]
        if self.use_regular_grid_interpolator:
            x_unique = np.unique(self.x_coord)
            y_unique = np.unique(self.y_coord)
            grid_values = values.reshape(len(x_unique), len(y_unique))
            interpolator = RegularGridInterpolator((x_unique, y_unique), grid_values)
            return interpolator(point)
        else:
            dist, idx = self.kd_tree.query(point)
            return values[idx]

    def mode_shapes_function(self, mode_number):
        values = self.values[mode_number]

        if self.use_regular_grid_interpolator:
            x_unique = np.unique(self.x_coord)
            y_unique = np.unique(self.y_coord)
            grid_values = values.reshape(len(x_unique), len(y_unique))
            interpolator = RegularGridInterpolator((x_unique, y_unique), grid_values)
            return interpolator
        else:
            def interpolator(point):
                dist, idx = self.kd_tree.query(point)
                return values[idx]
            return interpolator

    def plot(self, mode_number):
        mshape_to_plot = self.m_shapes[mode_number]
        fig = Figure()
        a = fig.add_subplot(1, 1, 1, projection='3d')
        a.plot_trisurf(self.x_coord, self.y_coord, mshape_to_plot, cmap=plt.cm.hsv,
                       linewidth=0, antialiased=False)
        return fig

    def geometry(self):
        fig = plt.figure()
        a = fig.add_subplot()

        plt.xlim([0, np.max(self.x_coord)])
        plt.ylim([0, np.max(self.y_coord)])

        plt.xlabel('X [m]')
        plt.ylabel('Y [m]')

        # a.scatter(self.x_coord, self.y_coord, s=2 )

        a.grid(which='minor', alpha=0.2)
        a.grid(which='major', alpha=0.8)
        a.axis(xmin=0, xmax=np.max(self.x_coord), ymin=0, ymax=np.max(self.y_coord))

        return fig, a

    def mode_scale(self, modes, recipient):
        ModeScale = np.zeros(len(modes))
        counter = 0

        for mode in modes:
            ModeScale[counter] = self.mode_shape_value(mode - 1, recipient)
            counter = counter + 1

        return ModeScale


class Path:
    """Klasa Path racuna pravolinijsku putanju pesaka definisanu pocetnom i krajnjom tackom"""

    def __init__(self, start, finish):
        self.length = np.sqrt((finish[0] - start[0]) ** 2 + (finish[1] - start[1]) ** 2)
        self.start = start
        self.finish = finish

        if self.length == 0:
            self.angle = 0
        elif (finish[0] - start[0]) != 0:

            tanalfa = (finish[1] - start[1]) / (finish[0] - start[0])

            if (finish[1] - start[1]) >= 0:
                if (finish[0] - start[0]) >= 0:
                    alfa = math.atan(np.abs(tanalfa))
                else:
                    alfa = - math.atan(np.abs(tanalfa)) + np.pi
            elif (finish[0] - start[0]) < 0:
                alfa = math.atan(np.abs(tanalfa)) - np.pi
            else:
                alfa = - math.atan(np.abs(tanalfa))

            self.angle = alfa

        else:
            if (finish[1] - start[1]) > 0:
                self.angle = np.pi / 2
            else:
                self.angle = 3 * np.pi / 2

    def lff_path(self, vp, t):

        path = np.zeros((2, len(t)))  # Putanja pesaka definisana u svakoj tacki vremenskog inkrementa
        path[0][:] = self.start[0] + vp * t * np.cos(self.angle)
        path[1][:] = self.start[1] + vp * t * np.sin(self.angle)

        return path

    def hff_path(self, fp, vp, step_length):

        nstep = int(self.length / step_length)  # Broj koraka koji pesak napravi
        if nstep == 0:  # Stacionarna sila
            nstep = 1

        tstep = np.zeros(nstep)  # Vremenski trenutak u kom pesak napravi odredjeni korak
        for step in range(nstep):
            tstep[step] = (step + 1) / fp

        path = np.zeros((2, nstep))  # Formiranje putanje pesaka, koja je definisana svakim korakom
        path[0][:] = self.start[0] + vp * tstep * np.cos(self.angle)
        path[1][:] = self.start[1] + vp * tstep * np.sin(self.angle)

        return path


class Pedestrian:
    def __init__(self, fp, g, l_step):
        self.frequency = fp
        self.weight = g
        self.step_length = l_step
        self.speed = self.frequency * self.step_length


def time_vector(length, speed, dt):
    T = length / speed
    t = np.arange(0, T, dt)
    return t


def floor_type(force_model, f1):
    if force_model == "Kerr" or force_model == "Rainer":
        limit_frequency = 10
    elif force_model == "Arup":
        limit_frequency = 10.5
    else:
        limit_frequency = 0

    if limit_frequency == 0:
        floor_type = "BOTH"

    else:
        if f1 <= limit_frequency:
            floor_type = "LFF"
        else:
            floor_type = "HFF"

    return floor_type


def foot_path(flr_type, path, pedestrian, t):
    if flr_type == "LFF":
        footpath = path.lff_path(pedestrian.speed, t)
    elif flr_type == "HFF":
        footpath = path.hff_path(pedestrian.frequency, pedestrian.speed, pedestrian.step_length)
    else:
        footpath = [None] * 2
        footpath[0] = path.lff_path(pedestrian.speed, t)
        footpath[1] = path.hff_path(pedestrian.frequency, pedestrian.speed, pedestrian.step_length)

    return footpath


def calculation(floor, force_input, zetta, start, finish, modes, fp, Go, stepLength, dt):
    path = Path(start, finish)
    pedestrian = Pedestrian(fp, Go, stepLength)

    flr_type = floor_type(force_input, floor.frequency[0])

    t = time_vector(path.length, pedestrian.speed, dt)
    damping = np.full(shape=len(floor.frequency), fill_value=zetta, dtype=float)

    ModeShapes = [None] * len(floor.frequency)
    for mode in range(len(floor.frequency)):
        ModeShapes[mode] = floor.mode_shapes_function(mode)

    footpath = foot_path(flr_type, path, pedestrian, t)

    response = ModalAnalysis(force_input, flr_type, modes, floor, damping, ModeShapes, pedestrian, footpath, t)

    return response, t


"""


file_path = 'D:\\Dropbox\\MM\\RADOVI\\2021 - RAD CLT Connections ABAQUS modeli\\MODELI\\Plocca 3x6\\Bez mase\\'

file = 'single_ploca_bez_mase.dat'  # dat fajl iz koga citamo broj cvorova, frekvencije i modalne mase
DatFile = open(file_path+file, "r")


dat_file, rpt_files, dat_name = read_files(file_path, "Abaqus CAE")

f = Floor(dat_file, rpt_files)
print(f.mmodal)
"""

# putanja = "C:\\Users\\Nikola Lakic\\Desktop\\Monolitna"
# print(read_files(putanja))
