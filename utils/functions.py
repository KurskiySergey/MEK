import numpy as np
from mek_types.enums import hex_data

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
    file_enc = int.from_bytes(filename.encode("utf-8"), byteorder="big")
    file_id = file_enc % 256
    return file_id

def parse_scq(data):
    scq = data[0]
    left_v = scq[:1]
    right_v = scq[1:]
    scq_status = array_to_int(left_v)
    scq_value = array_to_int(right_v)
    return scq_status, scq_value

