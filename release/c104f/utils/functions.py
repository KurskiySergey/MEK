import numpy as np
import c104
from c104f.config import SERVER_DIR
import os

def signal_function(size, mean, ampl = 50, std = 20, T = 1000):
    x = np.linspace(start=0, stop=size, num=size)
    i = 0
    f = np.zeros_like(x)
    while mean + i*T < size:
        f += ampl * np.exp(-(x-(mean + i*T))**2 / std)
        i += 1
    return f


def sin_function(size, ampl = 50, mean = 0, w = 10):
    x = np.linspace(start=0, stop=size, num=size)
    f = ampl * np.sin(w * x + mean)

    return f

def rect_signal(size, ampl = 50, mean = 0, width = 10, T = 20):
    f = np.zeros(shape=(size,))
    f_x = ampl * np.ones(shape=(width,))
    i = 0
    while mean + i*T < size:
        f[mean + i*T:mean + i*T + width] = f_x
        i += 1
    return f

def triangle_signal(size, ampl = 50, mean = 0, width = 10, T = 20):
    x = np.linspace(start=0, stop=size, num=size)
    f = np.zeros_like(x)
    i = 0
    left_width = width // 2
    H = ampl
    while mean + i*T < size:
        x_left = x[mean + i*T: mean + i*T + left_width]
        x_right = x[mean + i*T + left_width: mean + i*T + 2*left_width]
        k = H / left_width
        b_left = - k*x_left[0]
        b_right = k * x_right[-1]
        f_left = k * x_left + b_left
        f_right = - k * x_right + b_right
        f_i = np.concatenate([f_left, f_right])
        f[mean + i*T: mean + i*T + 2*left_width] = f_i
        i += 1

    return f

def array_to_int(data):
    dt_bytes = "".join(data[::-1])
    value = int(dt_bytes, 16)
    return value

def get_file_id(filename):
    files = os.listdir(SERVER_DIR)
    for file_id, sv_filename in enumerate(files):
        if filename == sv_filename:
            return file_id
    return -1

def get_elements_data(elements:str):
    return elements.split(" ")[:-1]

def bytes_to_int_list(data: bytes):
    # print(type(data), data)
    # print(data[0])
    dt = [byte for byte in data]
    return dt

def delete_ft(zero_point, nof, server_ft=None):

    if server_ft is None:
        server_ft = get_server_ft(zero_point)
        file_info = server_ft.pop(nof)
        file = file_info.file
        file.close()  # close filestream
        del file_info
    else:
        file_info = server_ft.pop(nof)
        file = file_info.file
        file.close()  # close filestream
        del file_info

def get_server(zero_point):
    return zero_point.station.server

def get_server_ft(zero_point):
    server = get_server(zero_point)
    return server.files_transfer

def get_file_info(zero_point, nof):
    server_ft = get_server_ft(zero_point)
    return server_ft.get(nof)


def get_zero_point(station):
    zero_point = station.get_point(io_address=0)
    if zero_point is None:
        zero_point = station.add_point(io_address=0, type=c104.Type.F_AF_NA_1)

    return zero_point

