import csv
import time
from threading import Thread

import numpy as np
import serial
from matplotlib import pyplot as plt
from serial import Serial
import seaborn as sns


class Application:
    def __init__(self, port: str, rows: int, cols: int):
        self.d_thread = None
        self.serial = None
        self.serial_port_init(port)
        self.sensor_size = (rows, cols)
        self.channels = rows * cols
        self.fig, self.ax = plt.subplots(1, 1)

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
        average = np.zeros(self.channels)

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
                average[i] = average_val
        pass

    def plot(self):
        pass

    def stop_plot(self):
        pass

    def data_thread(self, start, filename):
        word = []
        current_dz = np.zeros(self.channels)

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
                            raw_count.append(float(word[index]))
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
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
                writer.writerow(data_set)

    def write_to_csv(self, filename):
        channel_name = ['time']
        for i in range(self.channels):
            name = 'Channel' + str(i)
            channel_name.append(name)
        start_time = time.time()

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
            writer.writerow(channel_name)

        self.d_thread = Thread(target=self.data_thread, args=(start_time, filename))
        self.d_thread.start()

    def stop_write_to_csv(self, filename):
        pass
