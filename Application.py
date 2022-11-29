import csv
import time
from threading import Thread

import numpy as np
import serial
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp
import seaborn as sns

write_on = mp.Value("i", 0)

class Application:
    def __init__(self, port: str, rows: int, cols: int):
        self.p_process = None
        self.d_process = None
        self.serial = None
        self.serial_port_init(port)
        self.sensor_size = (rows, cols)
        self.channels = rows * cols
        self.fig, self.ax = plt.subplots(1, 1)
        self.average = None
        self.spectrum = None
        self.rawcount = None
        self.file = None
        self.obs = 0

        self.plot_on = mp.Value("i", False)
        # self.plot_on.acquire() # this locks the variable
        # self.plot_on.value = True # to change it
        # self.plot_on.release() # to unlock it
        self.start_time = None

    def start(self):
        self.d_process = mp.Process(target=self.get_data, args=(self.plot_on, write_on))
        self.d_process.start()

    def shutdown(self):
        pass

    def serial_port_init(self, port, baudrate=500000):
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=None,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        ser.isOpen()
        self.serial = ser

    def get_baseline(self):
        index = 0
        i = 0
        count = 0
        input_val = np.zeros((100, self.channels))
        self.average = np.zeros(self.channels)

        # record the first 100 points of the taxels as baseline
        while index < 100:
            line = self.serial.readline()
            data = line.decode()
            word = data.split(",")
            len_word = len(word)
            count = count + 1
            if len_word >= self.channels:  # check value
                try:
                    for i in range(self.channels):
                        input_val[index][i] = float(word[i])
                    index = index + 1
                finally:
                    pass

        # add taxles together and get the average of the 100 taxels
        for i in range(self.channels):
            total = 0
            for index in range(100):
                total = input_val[index][i] + total
                average_val = total / 100
                self.average[i] = average_val
        pass

    def plot(self):
        self.get_baseline()
        self.p_process = mp.Process(target=self.plot_worker)
        self.p_process.start()

        # while True:
        #     n = random.random() * 5
        #     print
        #     "main: put:", n
        #     queue.put(n)
        #     time.sleep(1.0)
        #
        # self.p_process = Thread(target=self.plot_thread)
        # self.p_process.start()

    def animate(self):
        plt.cla()
        index = 1
        ind = 0
        data = np.zeros((8, 8))  # should be 10 x 10
        for i in range(7, -1, -1):
            for j in range(7, -1, -1):
                data[j][i] = self.average[ind] - self.rawcount
                index = index + 7
                ind = ind + 1

        # make the heat map
        ax = sns.heatmap(data, vmin=0, vmax=1.5, cbar=False, cmap="YlOrBr", square=True)

    def plot_worker(self):
        ani1 = FuncAnimation(plt.gcf(), self.animate, interval=100, blit=False)
        plt.show()
        # make the heat map

    def stop_plot(self):
        self.p_process.kill()

    def get_data(self, write_on, plot_on):
        while True:  # this will not block other functions since it is on a different thread
            line = self.serial.readline()
            raw_count = []
            try:
                data = line.decode()
                word = data.split(",")
                index = 0
                if len(word) >= self.channels + 1:  # discard faulty data
                    for index in range(self.channels):
                        try:
                            # this is for just the observation
                            self.raw_count.append(float(word[index]))
                        except ValueError:
                            pass
                        finally:
                            pass
            except UnicodeDecodeError:
                pass
            finally:
                pass

            data_set = raw_count
            self.start_time = time.time()
            data_set.insert(0, time.time() - self.start_time)

            if write_on.value > 0:
                with open(self.file, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
                    writer.writerow(data_set)

    #
    # def csv_thread(self, start, j):
    #     data_set = raw_count
    #     data_set.insert(0, time.time() - start)
    #     with open(j, 'a', newline='') as csvfile:
    #         writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
    #         writer.writerow()

    def write_to_csv(self):
        channel_name = ['time']
        for i in range(self.channels):
            name = 'Channel' + str(i)
            channel_name.append(name)

        with open(self.file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
            writer.writerow(channel_name)

        self.start_time = time.time()
        write_on.acquire()
        write_on.value = 1
        write_on.release()
        # self.d_process = Thread(target=self.get_data, args=(start_time, j))
        # self.d_process.start()

    def stop_write_to_csv(self):
        write_on.acquire()
        write_on.value = 0
        write_on.release()
