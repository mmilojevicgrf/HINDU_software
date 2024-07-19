import math
from scipy.interpolate import RegularGridInterpolator
from hindu_calculation import *

np.seterr(divide='ignore')
import matplotlib.pyplot as plt

XCoord = None
YCoord = None


def get_cord():
    return globals()["Xcoord"], globals()["Ycoord"]


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


class Floor:
    """Klasa Floor sadrzi sve geometrijske i materijalne karakteristike tavanice ucitane iz Abaqusa"""

    def __init__(self, dat_file, rpt_files):
        self.NNode, self.frequency, self.modal_mass, self.m_shapes = modal_characteristics(dat_file, rpt_files)
        self.x_coord, self.y_coord = floor_geometry(self.NNode, rpt_files[0])
        self.modal_stiffness = (2 * np.pi * self.frequency) ** 2 * self.modal_mass
        self.xy = np.column_stack((self.x_coord, self.y_coord))
        self.x = np.unique(self.xy[:, 0])
        self.y = np.unique(self.xy[:, 1])

    def mode_shape_value(self, mode_number, point):
        values = self.m_shapes[mode_number].reshape(len(self.x), len(self.y))
        mode_interpolator = RegularGridInterpolator((self.x, self.y), values)
        return mode_interpolator((point[0], point[1]))

    def mode_shapes_function(self, mode_number):
        values = self.m_shapes[mode_number].reshape(len(self.x), len(self.y))
        mode_interpolator = RegularGridInterpolator((self.x, self.y), values)
        return mode_interpolator

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

#putanja = "C:\\Users\\Nikola Lakic\\Desktop\\Monolitna"
#print(read_files(putanja))
