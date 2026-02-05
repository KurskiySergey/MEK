import c104
import matplotlib.pyplot as plt
import numpy as np


class DataVisualize:
    def __init__(self, batch_size = 10, data_size = 100):
        self.cl_connection = None
        self.batch_data = None
        self.batch_size = batch_size
        self.data_size = data_size
        self.info = np.zeros(shape=(self.data_size))
        self.batch_count = self.data_size // self.batch_size
        if self.batch_count * self.batch_size < self.data_size:
            self.batch_count += 1

        self.line = None
        self.ax= None

    @property
    def connection(self):
        return self.cl_connection

    @connection.setter
    def connection(self, connection: c104.Connection):
        self.cl_connection = connection

    @property
    def set_batch(self):
        return self.batch_data

    @set_batch.setter
    def set_batch(self, batch: c104.Batch):
        self.batch_data = batch


    def update_data(self, batch_count):
        data_points = np.asarray([point.value for point in self.batch_data.points])
        if batch_count < self.batch_count:
            info_slice_shape = self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size].shape[0]
            self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size] = data_points[:info_slice_shape]


    def update_plot(self):
        self.line.set_ydata(self.info)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        plt.draw()
        plt.pause(0.01)


    def generate_plot(self):
        plt.ion()  # Turn on interactive mode

        # Use a deque to maintain a fixed-size window of data
        fig, ax = plt.subplots()
        line, = ax.plot(list(range(self.data_size)), self.info)
        ax.set_ylim(-100, 100)  # Set y-axis limit

        self.line = line
        self.ax = ax

        self.update_plot()

    def close_plot(self):
        plt.ioff()
        plt.show()


class MultiDataVisualize:
    def __init__(self, batch_size = 10):
        self.cl_connection = None
        self.batches = None
        self.batch_size = batch_size
        self.info = np.zeros(shape=(self.data_size))
        self.batch_count = self.data_size // self.batch_size
        if self.batch_count * self.batch_size < self.data_size:
            self.batch_count += 1

        self.line = None
        self.ax= None

    @property
    def connection(self):
        return self.cl_connection

    @connection.setter
    def connection(self, connection: c104.Connection):
        self.cl_connection = connection

    @property
    def set_batch(self):
        return self.batches

    @set_batch.setter
    def set_batch(self, batches):
        self.batches = batches


    def update_data(self, batch_count):
        data_points = np.asarray([point.value for point in self.batch_data.points])
        if batch_count < self.batch_count:
            info_slice_shape = self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size].shape[0]
            self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size] = data_points[:info_slice_shape]


    def update_plot(self):
        self.line.set_ydata(self.info)
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        plt.draw()
        plt.pause(0.01)


    def generate_plot(self):
        plt.ion()  # Turn on interactive mode

        # Use a deque to maintain a fixed-size window of data
        fig, ax = plt.subplots()
        line, = ax.plot(list(range(self.data_size)), self.info)
        ax.set_ylim(-100, 100)  # Set y-axis limit

        self.line = line
        self.ax = ax

        self.update_plot()

    def close_plot(self):
        plt.ioff()
        plt.show()