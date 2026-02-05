import c104
import matplotlib.pyplot as plt
import numpy as np
from mek_types.batch import StationsBatch


class DataVisualize:
    def __init__(self, batch_size = 10):
        self.cl_connection = None
        self.batch_size = batch_size
        self.batch_data = None
        self.info = np.zeros(shape=self.batch_size)

        self.line = None
        self.ax= None

    @property
    def connection(self):
        return self.cl_connection

    @connection.setter
    def connection(self, connection: c104.Connection):
        self.cl_connection = connection

    @property
    def monitor_batch(self):
        return self.batch_data

    @monitor_batch.setter
    def monitor_batch(self, batch: c104.Batch):
        self.batch_data = batch


    def update_data(self):
        data_points = np.asarray([point.value for point in self.batch_data.points])
        self.info = data_points
        # if batch_count < self.batch_count:
        #     info_slice_shape = self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size].shape[0]
        #     self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size] = data_points[:info_slice_shape]


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
        line, = ax.plot(list(range(self.batch_size)), self.info)
        ax.set_ylim(-100, 100)  # Set y-axis limit

        self.line = line
        self.ax = ax

        self.update_plot()

    def close_plot(self):
        plt.ioff()
        plt.close()


class MultiDataVisualize:
    def __init__(self, batch_size = 10, data_size = 100):
        self.cl_connection = None
        self.batch_data = None
        self.batch_size = batch_size
        self.data_size = data_size
        self.info = np.zeros(shape=self.data_size)
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
    def monitor_batch(self):
        return self.batch_data

    @monitor_batch.setter
    def monitor_batch(self, batch: c104.Batch):
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


class MultiStationVisualizer:
    def __init__(self, batch_size = 10, stations = 4, figsize = (12, 8), data_size = None):
        self.cl_connection = None
        self.batch_size = batch_size
        self.data_size = data_size
        self.batch_data = None
        self.figsize = figsize
        self.info = np.zeros(shape=(stations, self.batch_size))
        self.stations = stations
        self.lines = []
        self.axes= []
        self.batch_count = None
        if self.data_size is not None:
            self.batch_count = self.batch_size // self.data_size
            if self.batch_count * self.data_size < self.batch_size:
                self.batch_count += 1

    @property
    def connection(self):
        return self.cl_connection

    @connection.setter
    def connection(self, connection: c104.Connection):
        self.cl_connection = connection

    @property
    def monitor_batch(self):
        return self.batch_data

    @monitor_batch.setter
    def monitor_batch(self, batch: StationsBatch):
        self.batch_data = batch


    def update_data(self, step = None):
        if self.data_size is not None:
            data_points = np.asarray([[point.value for point in batch.points] for batch in self.batch_data.batches])
            if step < self.batch_count:
                info_slice_shape = self.info[:, step * self.data_size:(step + 1) * self.data_size].shape[1]
                print(f"patch {step}, patch_size: {info_slice_shape}, "
                      f"{info_slice_shape * (step + 1) if info_slice_shape == self.data_size else self.batch_size} / {self.batch_size}")
                self.info[:, step * self.data_size:(step + 1) * self.data_size] = data_points[:,
                    :info_slice_shape]
        else:
            data_points = np.asarray([[point.value for point in batch.points] for batch in self.batch_data.batches])
            self.info = data_points
        # if batch_count < self.batch_count:
        #     info_slice_shape = self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size].shape[0]
        #     self.info[batch_count*self.batch_size:(batch_count + 1) * self.batch_size] = data_points[:info_slice_shape]


    def update_plot(self):
        for i in range(self.stations):
            dt = self.info[i]
            line = self.lines[i]
            ax = self.axes[i]
            line.set_ydata(dt)
            ax.relim()
            ax.autoscale_view(True, True, True)
        plt.draw()
        plt.pause(0.01)

    def generate_plot(self):
        plt.ion()  # Turn on interactive mode
        row_count = 2
        column_count = self.stations // row_count
        if column_count * row_count < self.stations:
            column_count += 1
        # Use a deque to maintain a fixed-size window of data
        fig, axes = plt.subplots(nrows=row_count, ncols=column_count, figsize=self.figsize)
        axes = axes.reshape(row_count *column_count)
        for i in range(self.stations):
            ax = axes[i]
            line, = ax.plot(list(range(self.batch_size)), self.info[i])
            ax.set_ylim(-100, 100)  # Set y-axis limit

            self.lines.append(line)
            self.axes.append(ax)

        self.update_plot()

    def close_plot(self):
        plt.ioff()
        plt.close()