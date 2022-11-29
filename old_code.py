import matplotlib.pyplot as plt
import numpy as np
import serial
import seaborn as sns
import time
import csv

from threading import Thread
from matplotlib.animation import FuncAnimation

# **********************Global variables begin***************************#
# **********************USER DEFINED VALUES BEGIN******************#
file_name = "matrix_prox_Ch65_1.csv"

x_lim = 4  # number bar on the x axis
y_lim = 15  # number of bar on the y axis
z_lim = 50
# limit of z axis from z_lim to -z_lim
# Channels = x_lim*y_lim # number of channels
Channels = 100
stress_channels = 14
shear_channels = 4

x_space_ratio = 1
y_space_ratio = y_lim / x_lim
z_space_ratio = 1.5

bar_size_x = 0.5
bar_size_y = 0.5

offset_z = 300
offset_colour = offset_z - 300

# **********************USER DEFINED VALUES END******************#

# value that are going to change
dx = []  # 3d x value. does not change in our case
dy = []  # 3d y value. does not change in our case
current_dz = []
num = 0
dz = np.zeros(Channels)  # 3d z value. change relative to capacitance
stress_vals = np.zeros(stress_channels)
current_dz = np.zeros(Channels)
shear_vals_1 = np.zeros(shear_channels)
shear_vals_2 = np.zeros(shear_channels)
data = []
word = []
xedges = []  # the x location of each bar, generaged by x_lim
yedges = []  # the y location of each bar, generated by y_lim

y1 = 0
y2 = 0

input_val = []
total = []
average = []


# **********************Global variables end***************************#

# open the serial port
def serial_port_init():  # Serial port initializationst
    ser = serial.Serial(
        port='/dev/tty.usbmodem11103',
        baudrate=500000,
        timeout=None,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    ser.isOpen()
    return ser


# continue reading data from the serial port
def thread1():
    global word, current_dz, U, y1, y2  # some how python want global variable to be defined in function
    while True:  # this will not block other functions since it is on a different thread
        line = ser.readline()
        raw_count = []
        try:
            data = line.decode()
            word = data.split(",")
            index = 0
            if len(word) >= Channels + 1:  # discard faulty data
                for index in range(Channels):
                    try:
                        # this is for just the observation
                        raw_count.append(float(word[index]))

                        # this is for getting the baseline - calculating the difference
                        # dz[index] = ((average[index] - float(word[index]))/average[index])- calibrationArray[i]#- offset_z
                    except ValueError:
                        pass
                    finally:
                        pass
        except UnicodeDecodeError:
            pass
        finally:
            pass

        data_set = raw_count
        data_set.insert(0, time.time() - start)
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
            writer.writerow(data_set)


def animate1(num):
    plt.cla()
    index = 1
    ind = 0
    current_dz = sorting(dz)
    data = np.zeros((15, 4))  # should be 10 x 10
    for i in range(3, -1, -1):
        for j in range(14, -1, -1):
            data[j][i] = current_dz[ind]
            index = index + 3
            ind = ind + 1

    # make the heat map
    ax = sns.heatmap(data, vmin=0, vmax=1.5, cbar=False, cmap="YlOrBr", square=True)
    # Q.set_UVC(U, V)
    # ax.set_ylim(0,400)


def sorting(unsorted_list):
    sorted_list = np.multiply(1, unsorted_list)
    '''
    for index in range (60):
        if(sorted_list[index] < 40):
            sorted_list[index] = 0
    '''
    return sorted_list


if __name__ == "__main__":
    # ***********************Code start here**********************************#
    # Initialize serial port
    ser = serial_port_init()
    # Initialize settings for plotting
    # Create a string including Channel name
    channel_name = ['time']
    for i in range(Channels):
        name = 'Channel' + str(i)
        channel_name.append(name)

    # plt.ion()
    fig, ax = plt.subplots(1, 1)
    # fig.suptitle("Pressure")

    # Q = ax.quiver(X, Y, U, V, units = 'xy', scale = 1, color = "red", width = 2)
    data = np.zeros((1, 1))
    ax = sns.heatmap(data, vmin=0, vmax=200, cbar=False, cmap="YlOrBr")
    ax.set_xlim(-500, 500)
    ax.set_ylim(-500, 500)

    # define values for calculating average at the beginning
    index = 0
    i = 0
    count = 0
    input_val = np.zeros((100, Channels))
    average = np.zeros(Channels)

    # record the first 100 points of the taxels as baseline
    while index < 100:
        line = ser.readline()
        data = line.decode()
        word = data.split(",")
        len_word = len(word)
        count = count + 1
        if (len_word >= Channels):  # check value
            try:
                for i in range(Channels):
                    input_val[index][i] = float(word[i])
                index = index + 1
            finally:
                pass

    # add taxles together and get the average of the 100 taxels
    for i in range(Channels):
        total = 0
        for index in range(100):
            total = input_val[index][i] + total
            average_val = total / 100
            average[i] = average_val

    # Create a CSV file for recording the data

    start = time.time()
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
        writer.writerow(channel_name)

    # continue reading data from the serial
    thread = Thread(target=thread1)
    thread.start()

    ani1 = FuncAnimation(plt.gcf(), animate1, interval=100, blit=False)
    # ani2 = FuncAnimation(plt.gcf(), animate2,interval=100, blit = False)
    plt.show()