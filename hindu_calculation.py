import numpy as np
from matplotlib.figure import Figure


def newmark_int(time, force, u0, udot0, mass, stiffness, damp):

    gam = 1/2
    beta = 1/4

    wn = np.sqrt(stiffness/mass)
    if len(time) == 0:
        u = 0
        udot = 0
        u2dot = 0
    else:

        dtime = time[1] - time[0]
        c = 2*damp*wn*mass

        kgor = stiffness + gam/beta/dtime*c + mass/beta/dtime ** 2
        a = mass/beta/dtime+gam*c/beta
        b = 0.5*mass/beta + dtime*(0.5*gam/beta - 1)*c

        df = np.diff(force)

        u = np.zeros(len(time))
        udot = np.zeros(len(time))
        u2dot = np.zeros(len(time))

        u[0] = u0
        udot[0] = udot0
        u2dot[0] = 1/mass*(force[0] - stiffness*u0 - c*udot0)

        for i in range(len(time)-1):
            dforce = df[i] + a*udot[i] + b*u2dot[i]
            du_i = dforce/kgor
            dudot_i = gam/beta/dtime*du_i-gam/beta*udot[i]+dtime*(1-0.5*gam/beta)*u2dot[i]
            du2dot_i = 1/beta/dtime**2*du_i - 1/beta/dtime*udot[i]-0.5/beta*u2dot[i]

            u[i+1] = du_i + u[i]
            udot[i + 1] = dudot_i + udot[i]
            u2dot[i + 1] = du2dot_i + u2dot[i]

    return [u, udot, u2dot]


def impulse_vib(lenT, dt, y0, ydot0, freq, zeta):

    t = np.arange(0, lenT * dt, dt)
    w = freq * 2 * np.pi
    wd = w * np.sqrt(1 - zeta ** 2)
    epsilon = zeta * w

    if ydot0 >= 0:

        c = np.sqrt(y0 ** 2 + ((ydot0 + epsilon * y0)/wd) ** 2)
    else:
        c = - np.sqrt(y0 ** 2 + ((ydot0 + epsilon * y0)/wd) ** 2)
    alfa = 0

    y = c * np.exp(- epsilon * t) * np.sin(wd * t + alfa)
    ydot = c * np.exp(- epsilon * t) * (-epsilon * np.sin(wd * t + alfa) + wd * np.cos(wd * t + alfa))
    y2dot = c * np.exp(- epsilon * t) * ((epsilon ** 2 - wd ** 2) * np.sin(wd * t + alfa) - 2 * epsilon * wd * np.cos(wd * t + alfa))

    return [y, ydot, y2dot]


class ImpulseLoad:

    def __init__(self, fp, fn):

        self.impulse = 54 * fp ** 1.43 / fn ** 1.3


class HarmonicForce:

    def __init__(self, name, pedestrian, t):

        if name == "Kerr":
            self.number_of_harmonics = 3

        elif name == "Arup" or name == "Rainer":
            self.number_of_harmonics = 4

        elif name == "Živanović":
            self.number_of_harmonics = 5

        self.force = np.zeros((self.number_of_harmonics, len(t)))

        for harmonic in range(self.number_of_harmonics):
            self.force[harmonic][:] = pedestrian.weight * np.sin((harmonic + 1) * 2 * np.pi * pedestrian.frequency * t)


class Arup(HarmonicForce):

    def __init__(self, pedestrian, t):

        HarmonicForce.__init__(self, "Arup", pedestrian, t)

        alpha = np.zeros(self.number_of_harmonics)
        alpha[0] = 0.41 * (pedestrian.frequency - 0.95)
        if alpha[0] > 0.56:
            alpha[0] = 0.56
        alpha[1] = 0.0056 * (2 * pedestrian.frequency + 12.3)
        alpha[2] = 0.0064 * (3 * pedestrian.frequency + 5.2)
        alpha[3] = 0.0065 * (4 * pedestrian.frequency + 2)

        for harmonic in range(self.number_of_harmonics):
            self.force[harmonic][:] = self.force[harmonic][:] * alpha[harmonic]


class Rainer(HarmonicForce):

    def __init__(self, pedestrian, t):
        HarmonicForce.__init__(self, "Rainer", pedestrian, t)

        alpha = np.zeros(self.number_of_harmonics)
        alpha[0] = \
            -0.0349 * pedestrian.frequency ** 6 + 0.7037 * pedestrian.frequency ** 5 - 4.7273 * pedestrian.frequency ** 4 + 14.691 * pedestrian.frequency ** 3 - 23.014 * pedestrian.frequency ** 2 + \
            17.877 * pedestrian.frequency - 5.4404
        alpha[1] = \
            0.0015 * (2 * pedestrian.frequency) ** 6 - 0.0293 * (2 * pedestrian.frequency) ** 5 + 0.2218 * (2 * pedestrian.frequency) ** 4 - 0.7966 * (2 * pedestrian.frequency) ** 3 + \
            1.3527 * (2 * pedestrian.frequency) ** 2 - 0.8426 * (2 * pedestrian.frequency)
        alpha[2] = \
            -2E-05 * (3 * pedestrian.frequency) ** 6 + 0.0006 * (3 * pedestrian.frequency) ** 5 - 0.009 * (3 * pedestrian.frequency) ** 4 + 0.0656 * (3 * pedestrian.frequency) ** 3 - \
            0.2477 * (3 * pedestrian.frequency) ** 2 + 0.4834 * (3 * pedestrian.frequency) - 0.3618
        alpha[3] = \
            1.29633304e-04 * (4 * pedestrian.frequency) ** 6 - 4.78806612e-03 * (4 * pedestrian.frequency) ** 5 + 7.19702441e-02 * (4 * pedestrian.frequency) ** 4 - \
            5.64226168e-01 * (4 * pedestrian.frequency) ** 3 + 2.43909154e+00 * (4 * pedestrian.frequency) ** 2 - 5.52723486 * (4 * pedestrian.frequency) + 5.18293170

        for harmonic in range(self.number_of_harmonics):
            self.force[harmonic][:] = self.force[harmonic][:] * alpha[harmonic]


class Kerr(HarmonicForce):

    def __init__(self, pedestrian, t):
        HarmonicForce.__init__(self, "Kerr", pedestrian, t)

        alpha = np.zeros(self.number_of_harmonics)
        alpha[0] = -0.2649 * pedestrian.frequency ** 3 + 1.3206 * pedestrian.frequency ** 2 - 1.7597 * pedestrian.frequency + 0.7613
        alpha[1] = 0.07
        alpha[2] = 0.05

        for harmonic in range(self.number_of_harmonics):
            self.force[harmonic][:] = self.force[harmonic][:] * alpha[harmonic]


class StanaForce(HarmonicForce):

    def __init__(self, pedestrian, t):
        HarmonicForce.__init__(self, "Živanović", pedestrian, t)

        alpha = np.zeros(self.number_of_harmonics)
        alpha[0] = -0.2649 * pedestrian.frequency ** 3 + 1.3206 * pedestrian.frequency ** 2 - 1.7597 * pedestrian.frequency + 0.7613
        alpha[1] = 0.07
        alpha[2] = 0.05
        alpha[3] = 0.05
        alpha[4] = 0.03

        for harmonic in range(self.number_of_harmonics):
            self.force[harmonic][:] = self.force[harmonic][:] * alpha[harmonic]


def harmonic_force(force_model, pedestrian, t):

    if force_model == "Kerr":

        force = Kerr(pedestrian, t)

    elif force_model == "Arup":

        force = Arup(pedestrian, t)

    elif force_model == "Rainer":
        force = Rainer(pedestrian, t)

    elif force_model == "Živanović":
        force = StanaForce(pedestrian, t)
    else:
        force = np.zeros(len(t))

    return force


class LffResponse:
    def __init__(self, standard, floor_type, modes, floor, damping, mode_shape, pedestrian, path, t):

        if floor_type == "LFF":

            force = harmonic_force(standard, pedestrian, t)

            y = np.zeros((force.number_of_harmonics, len(modes), len(t)))
            ydot = np.zeros((force.number_of_harmonics, len(modes), len(t)))
            y2dot = np.zeros((force.number_of_harmonics, len(modes), len(t)))

            y0 = 0  # Pocetno pomeranje
            ydot0 = 0  # Pocetna brzina

            modal_force = np.zeros((force.number_of_harmonics, len(t)))

            u = np.zeros((len(modes), len(t)))
            udot = np.zeros((len(modes), len(t)))
            u2dot = np.zeros((len(modes), len(t)))

            modescale = np.zeros((len(modes), len(t)))  # Ordinate ModeShape-a duz putanje pesaka

            for harmonic in range(force.number_of_harmonics):
                counter = 0
                for mode in modes:
                    if mode == 0:
                        counter = counter + 1
                        continue
                    else:
                        ms = mode_shape[mode-1]
                        for node in range(len(t)):
                            modescale[counter][node] = ms(path[0][node], path[1][node])
                            modal_force[harmonic][node] = force.force[harmonic][node] * modescale[counter][node]
                        [y[harmonic][counter][:], ydot[harmonic][counter][:], y2dot[harmonic][counter][:]] = \
                            newmark_int(t, modal_force[harmonic][:], y0, ydot0, floor.modal_mass[mode-1], floor.modal_stiffness[mode-1],
                                    damping[mode-1])

                        counter = counter + 1

                u = u + y[harmonic][:][:]
                udot = udot + ydot[harmonic][:][:]
                u2dot = u2dot + y2dot[harmonic][:][:]

            self.displacement_modes = u
            self.velocity_modes = udot
            self.acceleration_modes = u2dot

            self.displacement_harm = y
            self.velocity_harm = ydot
            self.acceleration_harm = y2dot

        else:

            print("Ovaj model sile se primenjuje samo na niskofrekventne tavanice")


class HffResponse:
    def __init__(self, floor_type, modes, floor, damping, mode_shape, pedestrian, path, t):
        if floor_type == "LFF":

            print("Ovaj model sile se primenjuje samo na visokofrekventne tavanice")

        else:

            period = t[-1]
            dt = t[1] - t[0]

            y = np.zeros((len(modes), len(t)))
            ydot = np.zeros((len(modes), len(t)))
            y2dot = np.zeros((len(modes), len(t)))

            self.displacement_harm = np.zeros((2, len(modes), len(t)))
            self.velocity_harm = np.zeros((2, len(modes), len(t)))
            self.acceleration_harm = np.zeros((2, len(modes), len(t)))

            nstep = len(path[1])
            y0 = np.zeros((nstep, len(modes)))  # Pocetno pomeranje pri svakom koraku
            ydot0 = np.zeros((nstep, len(modes)))  # Pocetna brzina pri svakom koraku

            counter = 0
            for mode in modes:
                if mode == 0:
                    continue
                else:
                    i_eff = ImpulseLoad(pedestrian.frequency, floor.frequency[mode-1])
                ms = mode_shape[mode-1]

                for step in range(nstep):

                    ydot0[step][counter] = ms(path[0][step], path[1][step]) * i_eff.impulse / floor.modal_mass[mode-1]

                    # formiranje matrice pocetnih brzina koje poticu od impulsnog opterecenja, za svaki korak i  ton

                    # Racunanje odgovora usled svakog koraka (1 korak = 1 impuls)
                    walk_time = np.arange((step + 1) / pedestrian.frequency, period, dt)
                    # vreme od pocetka koraka/impulsa do kraja putanje

                    [u, udot, u2dot] = \
                        impulse_vib(len(walk_time), dt, y0[step][counter], ydot0[step][counter], floor.frequency[mode-1],
                                    damping[mode-1])

                    for point in range(len(walk_time)):  # Superpozicija odgovara usled svakog koraka
                        y[counter][len(t) - point - 1] = y[counter][len(t) - point - 1] + u[len(walk_time) - point - 1]
                        ydot[counter][len(t) - point - 1] = \
                            ydot[counter][len(t) - point - 1] + udot[len(walk_time) - point - 1]
                        y2dot[counter][len(t) - point - 1] = \
                            y2dot[counter][len(t) - point - 1] + u2dot[len(walk_time) - point - 1]

                counter = counter + 1

            self.displacement_modes = y
            self.velocity_modes = ydot
            self.acceleration_modes = y2dot

            self.displacement_harm[0][:][:] = y
            self.velocity_harm[0][:][:] = ydot
            self.acceleration_harm[0][:][:] = y2dot


class Stana:
    def __init__(self, modes, floor, damping, mode_shape, pedestrian, path, t):

        self.displacement_harm = np.zeros((2, len(modes), len(t)))
        self.velocity_harm = np.zeros((2, len(modes), len(t)))
        self.acceleration_harm = np.zeros((2, len(modes), len(t)))

        modes_lff = [None] * len(modes)
        modes_hff = [None] * len(modes)
        counter = 0
        for mode in modes:
            if floor.frequency[mode-1] <= 12:
                modes_lff[counter] = mode
            else:
                modes_lff[counter] = int(0)

            if floor.frequency[mode-1] > 10:
                modes_hff[counter] = mode
            else:
                modes_hff[counter] = int(0)
            counter = counter + 1

        response_lff = LffResponse("Živanović", "LFF", modes_lff, floor, damping, mode_shape, pedestrian, path[0], t)
        response_hff = HffResponse("HFF", modes_hff, floor, damping, mode_shape, pedestrian, path[1], t)

        self.displacement_modes = response_lff.displacement_modes + response_hff.displacement_modes
        self.velocity_modes = response_lff.velocity_modes + response_hff.velocity_modes
        self.acceleration_modes = response_lff.acceleration_modes + response_hff.acceleration_modes

        self.displacement_harm[0][:][:] = self.displacement_modes
        self.velocity_harm[0][:][:] = self.velocity_modes
        self.acceleration_harm[0][:][:] = self.acceleration_modes


def arup(floor_type, modes, floor, damping, mode_shape, pedestrian, path, t):

    if floor_type == "LFF":

        response = LffResponse("Arup", floor_type, modes, floor, damping, mode_shape, pedestrian, path, t)
    else:
        response = HffResponse(floor_type, modes, floor, damping, mode_shape, pedestrian, path, t)

    return response


class ModalAnalysis:

    def __init__(self, standard, floor_type, modes, floor, damping, mode_shape, pedestrian, path, t):

        if standard == "Arup":
            response = arup(floor_type, modes, floor, damping, mode_shape, pedestrian, path, t)
        elif standard == "Kerr" or standard == "Rainer":
            response = LffResponse(standard, floor_type, modes, floor, damping, mode_shape, pedestrian, path, t)
        elif standard == "Živanović":
            response = Stana(modes, floor, damping, mode_shape, pedestrian, path, t)

        self.displacement_modes = response.displacement_modes
        self.velocity_modes = response.velocity_modes
        self.acceleration_modes = response.acceleration_modes

        self.displacement_harm = response.displacement_harm
        self.velocity_harm = response.velocity_harm
        self.acceleration_harm = response.acceleration_harm


class Response:

    def __init__(self, y, mode_shape_value):

        nmodes = len(mode_shape_value)

        if len(y[0]) > 100:

            n = len(y[0])
        else:
            n = len(y[1])

        self.mode_response = np.zeros((nmodes, n))
        for mode in range(nmodes):
            self.mode_response[mode] = y[mode] * mode_shape_value[mode]

        self.total_response = np.zeros(n)
        for mode in range(nmodes):
            self.total_response = self.total_response + self.mode_response[mode]


class Displacement(Response):
    pass


class Velocity(Response):
    pass


class Acceleration(Response):
    pass


def plot_total_response(type, response, time):

    fig = Figure()

    # font = {'fontname': 'Times New Roman'}

    a = fig.add_subplot()

    # a.xlabel('Time [s]', fontsize=24, **font)
    # a.ylabel(type, fontsize=24, **font)
    # a.xticks(fontsize=22, **font)
    # a.yticks(fontsize=22, **font)
    # a.set_xlim([0, time[-1]])
    a.plot(time, response.total_response)

    return fig


def plot_mode_response(type, response, time, modes):

    fig = Figure()

    # font = {'fontname': 'Times New Roman'}

    a = fig.add_subplot()

    counter = 0
    for mode in modes:
        a.plot(time, response.mode_response[counter][:], label="MODE " + str(mode))
        counter = counter + 1
    a.legend()

    # a.xlabel('Time [s]', fontsize=24, **font)
    # a.ylabel(type, fontsize=24, **font)
    # a.xticks(fontsize=22, **font)
    # a.yticks(fontsize=22, **font)
    # a.set_xlim([0, time[-1]])

    return fig


def plot_all_response(type, response, time, modes):

    fig = Figure()

    # font = {'fontname': 'Times New Roman'}

    a = fig.add_subplot()
    a.plot(time, response.total_response, label="Total response")
    counter = 0
    for mode in modes:
        a.plot(time, response.mode_response[counter][:], label="MODE " + str(mode))
        counter = counter + 1
    a.legend()

    # a.xlabel('Time [s]', fontsize=24, **font)
    # a.ylabel(type, fontsize=24, **font)
    # a.xticks(fontsize=22, **font)
    # a.yticks(fontsize=22, **font)
    # a.set_xlim([0, time[-1]])

    return fig


def plot_rms_response(type, response, time, rms):

    fig = Figure()

    # font = {'fontname': 'Times New Roman'}

    if type == "Acceleration [m/s^2]":
        label_rms = "Moving average T=1s"
    else:
        label_rms = "Moving average T=1step"

    a = fig.add_subplot()
    a.plot(time, response.total_response, label="Total response")
    a.plot(rms.time, rms.moving_average, label=label_rms)
    a.legend()

    # a.xlabel('Time [s]', fontsize=24, **font)
    # a.ylabel(type, fontsize=24, **font)
    # a.xticks(fontsize=22, **font)
    # a.yticks(fontsize=22, **font)
    # a.set_xlim([0, time[-1]])

    return fig


class MovingAverage1s:

    def __init__(self, a, t, mode_scale):

        number_of_harmonics = len(a)

        nmodes = len(a[1])

        a_harm = np.zeros((number_of_harmonics, len(t)))

        for harmonic in range(number_of_harmonics):
            for mode in range(nmodes):
                a_harm[harmonic][:] = a_harm[harmonic][:] + a[harmonic][mode][:] * mode_scale[mode]

        time = 1
        dt = t[1] - t[0]
        n = int(len(t) - time / dt)  # broj rms-a koje se mogu izvesti

        acc = np.zeros((number_of_harmonics, int(time / dt + 1)))  # vektor ubrzanja u okviru perioda T za sve harmonike
        average_harmonic = np.zeros((number_of_harmonics, n))  # moving average za sve harmonike
        time_vector = np.zeros((number_of_harmonics, n))

        for harmonic in range(number_of_harmonics):
            for i in range(n):
                # PROVERITI SA MARIJOM DA LI SE DOBIJAJU ISTE VREDNOSTI
                # for j in range(len(acc[1])):
                #     acc[harmonic][j] = a_harm[harmonic][i + j - 1]
                acc[harmonic] = a_harm[harmonic, i: i + len(acc[1])]
                average_harmonic[harmonic][i] = np.sqrt(np.mean(acc[harmonic][:] ** 2))
                time_vector[harmonic][i] = t[i]

        average = np.zeros(n)

        for harmonic in range(number_of_harmonics):
            average = average + (average_harmonic[harmonic][:]) ** 2

        self.moving_average = np.sqrt(average)
        self.time = time_vector[0][:]


class MovingAverage1step:

    def __init__(self, v, t, fp):

        time = 1/fp
        dt = t[1] - t[0]

        n = int(len(t) - time / dt)  # broj rms-a koje se mogu izvesti
        v_rms = np.zeros(n)
        velocity = np.zeros(int(time / dt + 1))  # vektor ubrzanja u okviru perioda T za sve harmonike
        time_vector = np.zeros(n)
        for i in range(n):
            for j in range(len(velocity)):
                velocity[j] = v[i + j - 1]
            v_rms[i] = np.sqrt(np.mean(velocity[:] ** 2))
            time_vector[i] = t[i]

        self.moving_average = v_rms
        self.time = time_vector
