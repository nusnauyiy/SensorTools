import csv
import queue
import time
from enum import Enum
from threading import Thread
from typing import Tuple

import numpy as np
import serial
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import multiprocessing as mp
import seaborn as sns

signalQueue = mp.Queue()
dataQueue = mp.Queue()

class Signal(Enum):
    CSV_START = 1
    CSV_STOP = 2
    PLOT_START = 3
    PLOT_STOP = 4

class Application:

    def __init__(self, port: str, rows: int, cols: int):
        self.port = port
        self.p_process = None
        self.d_process = None
        self.serial = None
        self.sensor_size = (rows, cols)
        self.channels = rows * cols
        self.fig, self.ax = plt.subplots(1, 1)
        data = np.zeros((1, 1))
        self.ax = sns.heatmap(data, vmin=0, vmax=200, cbar=False, cmap="YlOrBr")
        self.average = None
        self.spectrum = None
        # self.raw_count = []
        self.file = None
        self.obs = 0

        # self.plot_on.acquire() # this locks the variable
        # self.plot_on.value = True # to change it
        # self.plot_on.release() # to unlock it
        self.start_time = None

    def start(self):
        self.get_baseline()
        global signalQueue
        self.d_process = mp.Process(target=self.get_data, args=(signalQueue,))
        self.d_process.start()

    def shutdown(self):
        self.d_process.kill()
        # self.p_process.kill()

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
        self.serial_port_init(self.port)
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
        self.serial.close()
        # add taxles together and get the average of the 100 taxels
        for i in range(self.channels):
            total = 0
            for index in range(100):
                total = input_val[index][i] + total
                average_val = total / 100
                self.average[i] = average_val
        pass

    def plot(self, dataQueue):
        self.p_process = mp.Process(target=self.plot_worker, args=(dataQueue,))

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

    def animate(self, num, q):
        raw_count = q.get()
        # if len(raw_count) != self.channels + 1:
        #     pass
        # index = 1
        ind = 0
        data = np.zeros(self.sensor_size)  # should be 10 x 10
        row = self.sensor_size[0]
        col = self.sensor_size[1]

        print("FROM ANIMATE")
        # print(self.average)
        print(raw_count)
        for i in range(row - 1, -1, -1):
            for j in range(col - 1, -1, -1):
                data[j][i] = self.average[ind] - raw_count[ind]
                # index = index + 7
                ind = ind + 1
        # make the heat map
        self.ax = sns.heatmap(data, vmin=0, vmax=2000, cbar=False, cmap="YlOrBr", square=True)

    def plot_worker(self, q):
        # while True:
        #     item = q.get(block=True)
        #     print("FROM QUEUE")
        #     print(item)
        while True:
            ani1 = FuncAnimation(plt.gcf(), self.animate, fargs=(q,), interval=1, blit=False)
            plt.show()
            print("plotted?")
        # make the heat map

    def stop_plot(self):
        self.p_process.kill()

    def get_data(self, signalQ):
        self.serial_port_init(self.port)
        write_on = False
        plot_on = False
        dataQ = mp.Queue()
        self.plot(dataQ)
        while True:  # this will not block other functions since it is on a different thread
            try:
                item = signalQ.get(block=False)
                match item:
                    case Signal.CSV_START:
                        write_on = True
                    case Signal.CSV_STOP:
                        write_on = False
                    case Signal.PLOT_START:
                        plot_on = True
                    case Signal.PLOT_STOP:
                        plot_on = False
            except queue.Empty:
                pass
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
                            raw_count.append(float(word[index]))
                        except ValueError:
                            pass
                        finally:
                            pass
            except UnicodeDecodeError:
                pass
            finally:
                pass

            if len(raw_count) == self.channels:
                dataQ.put(raw_count)
            data_set = raw_count
            self.start_time = time.time()
            data_set.insert(0, time.time() - self.start_time)
            # print(raw_count)

            if write_on:
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
        signalQueue.put(Signal.CSV_START)
        # self.d_process = Thread(target=self.get_data, args=(start_time, j))
        # self.d_process.start()

    def stop_write_to_csv(self):
        global write_on
        write_on = False
