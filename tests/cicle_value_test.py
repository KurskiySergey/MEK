import c104
import datetime
import time
import random

from numpy.ma.core import count

from tests.client_visualize import DataVisualize

# c104.set_debug_mode(c104.Debug.Server|c104.Debug.Client|c104.Debug.Connection|c104.Debug.Point|c104.Debug.Callback)
# print("DEBUG MODE: {0}".format(c104.get_debug_mode()))

def create_client():
    test_client = c104.Client(tick_rate_ms=100, command_timeout_ms=10000)
    test_client.originator_address = 123
    return test_client

def create_connections(client: c104.Client):
    ip = "127.0.0.1"
    port = 2404
    connection = client.add_connection(ip, port, init=c104.Init.ALL)
    connection.protocol_parameters.connection_timeout = 20
    connection.protocol_parameters.message_timeout = 20
    connection.protocol_parameters.confirm_interval = 10
    connection.protocol_parameters.keep_alive_interval = 20

    return connection

def add_client_handlers(client:c104.Client):
    client.on_new_station(callable=cl_on_new_station)
    client.on_station_initialized(callable=cl_on_station_initialized)
    client.on_new_point(callable=cl_on_new_point)

    return client

def add_connection_handlers(connection:c104.Connection):
    connection.on_receive_raw(callable=cl_ct_on_receive_raw)
    connection.on_send_raw(callable=cl_ct_on_send_raw)

    return connection

## CLIENT HANDLERS
INIT_COUNT = {}
# get point info
def cl_pt_on_receive_point(point: c104.Point, previous_info: c104.Information, message: c104.IncomingMessage) -> c104.ResponseState:
    print("CL] {0} REPORT on IOA: {1} , message: {2}, previous: {3}, current: {4}".format(point.type, point.io_address, message, previous_info, point.info))
    # print("{0}".format(message.is_negative))
    # print("-->| POINT: 0x{0} | EXPLAIN: {1}".format(message.raw.hex(), c104.explain_bytes(apdu=message.raw)))
    return c104.ResponseState.SUCCESS

# create new station at connection
def cl_on_new_station(client: c104.Client, connection: c104.Connection, common_address: int) -> None:
    print("CL] NEW STATION {0} | CLIENT OA {1}".format(common_address, client.originator_address))
    connection.add_station(common_address=common_address)

# on initialize operation
def cl_on_station_initialized(client: c104.Client, station: c104.Station, cause: c104.Coi) -> None:
    global INIT_COUNT
    curr = INIT_COUNT.get(station.common_address, 0) # get info by station adress
    INIT_COUNT[station.common_address] = curr + 1 # update init count
    print("STATION {0} INITIALIZED due to {1} | INIT COUNT {2} | CLIENT OA {3}".format(station.common_address, cause, INIT_COUNT, client.originator_address))

# on creating new point
def cl_on_new_point(client: c104.Client, station: c104.Station, io_address: int, point_type: c104.Type) -> None:
    print("CL] NEW POINT: {1} with IOA {0} | CLIENT OA {2}".format(io_address, point_type, client.originator_address))
    point = station.add_point(io_address=io_address, type=point_type) # add point to the station
    point.on_receive(callable=cl_pt_on_receive_point) # add recieve callback from client

def cl_ct_on_receive_raw(connection: c104.Connection, data: bytes) -> None:
    print("client receive message")
    print("CL] -->| {1} [{0}] | CONN OA {2}".format(data.hex(), c104.explain_bytes_dict(apdu=data), connection.originator_address))

def cl_ct_on_send_raw(connection: c104.Connection, data: bytes) -> None:
    print("client send message")
    print("CL] <--| {1} [{0}] | CONN OA {2}".format(data.hex(), c104.explain_bytes_dict(apdu=data), connection.originator_address))

### SERVER HANDLERS

def sv_on_connect(server: c104.Server, ip: str) -> bool:
    print("server on connect")
    print("SV] <->| {0} | SERVER {1}:{2}".format(ip, server.ip, server.port))
    return ip == "127.0.0.1"


def sv_on_receive_raw(server: c104.Server, data: bytes) -> None:
    print("server receive message")
    print("SV] -->| {1} [{0}] | SERVER {2}:{3}".format(data.hex(), c104.explain_bytes(apdu=data), server.ip, server.port))


def sv_on_send_raw(server: c104.Server, data: bytes) -> None:
    print("server send message")
    print("SV] <--| {1} [{0}] | SERVER {2}:{3}".format(data.hex(), c104.explain_bytes(apdu=data), server.ip, server.port))


def sv_on_clock_sync(server: c104.Server, ip: str, date_time: datetime.datetime) -> c104.ResponseState:
    print("SV] ->@| Time {0} from {1} | SERVER {2}:{3}".format(date_time, ip, server.ip, server.port))
    return c104.ResponseState.SUCCESS


def sv_on_unexpected_message(server: c104.Server, message: c104.IncomingMessage, cause: c104.Umc) -> None:
    print("SV] ->?| {1} from CLIENT OA {0} | SERVER {2}:{3}".format(message.originator_address, cause, server.ip, server.port))


def create_server():
    my_server = c104.Server(ip="0.0.0.0", port=2404, tick_rate_ms=100, max_connections=10)
    my_server.max_connections = 100
    my_server.protocol_parameters.connection_timeout = 20
    my_server.protocol_parameters.message_timeout = 20
    my_server.protocol_parameters.confirm_interval = 10
    my_server.protocol_parameters.keep_alive_interval = 20

    return my_server

def add_server_handlers(server: c104.Server):
    server.on_receive_raw(callable=sv_on_receive_raw)
    server.on_send_raw(callable=sv_on_send_raw)
    server.on_connect(callable=sv_on_connect)
    server.on_clock_sync(callable=sv_on_clock_sync)
    server.on_unexpected_message(callable=sv_on_unexpected_message)

    return server

def create_measure(station: c104.Station):
    sv_measurement_point = station.add_point(io_address=11, type=c104.Type.M_ME_NC_1, report_ms=1000)
    sv_measurement_point.value = float(12.34)
    sv_measurement_point.on_before_auto_transmit(callable=on_before_auto_transmit_step)

    return sv_measurement_point

def create_measure_step_command(station: c104.Station, sv_measure: c104.Point):
    sv_command_point = station.add_point(io_address=12, type=c104.Type.C_SE_NC_1, report_ms=0,
                                              related_io_address=sv_measure.io_address,
                                              related_io_autoreturn=True,
                                              command_mode=c104.CommandMode.SELECT_AND_EXECUTE)
    sv_command_point.on_receive(callable=on_setpoint_command)

    return sv_command_point

def on_before_auto_transmit_step(point: c104.Point) -> None:
    print("SV] {0} PERIODIC TRANSMIT on IOA: {1}".format(point.type, point.io_address))
    point.value = float(random.randint(-64, 63))  # import random

def on_setpoint_command(point: c104.Point, previous_info: c104.Information, message: c104.IncomingMessage) -> c104.ResponseState:
    print("SV] {0} SETPOINT COMMAND on IOA: {1}, new: {2}, prev: {3}, cot: {4}, quality: {5}".format(point.type, point.io_address, point.value, previous_info, message.cot, point.quality))
    if point.related_io_address:
        print("SV] -> RELATED IO ADDRESS: {}".format(point.related_io_address))
        # related_point = sv_station_2.get_point(point.related_io_address)
        # if related_point:
        #     print("SV] -> RELATED POINT VALUE UPDATE")
        #     related_point.value = point.value
        # else:
        #     print("SV] -> RELATED POINT NOT FOUND!")
    return c104.ResponseState.SUCCESS

def cl_point_on_recieve(point: c104.Point, previous_info: c104.Information, message: c104.IncomingMessage) -> c104.ResponseState:
    print(point.value)
    return c104.ResponseState.SUCCESS

def cl_point_on_read(point:c104.Point)->None:
    print("SV] {0} READ COMMAND on IOA: {1}".format(point.type, point.io_address))
    print(point.value)

def create_batch(station: c104.Station, bathc_size: int, start_io = 100):
    start_io = start_io
    count = bathc_size
    batch = c104.Batch(cause=c104.Cot.SPONTANEOUS)
    for i in range(count):
        point_i = station.add_point(io_address=start_io + i, type=c104.Type.M_ME_NC_1, report_ms=0)
        point_i.value = float(random.randint(-63, 64))
        point_i.on_before_read(callable=cl_point_on_read)
        point_i.on_before_auto_transmit(callable=on_before_auto_transmit_step)
        batch.add_point(point_i)

    return batch

def main():
    data_size = 7000
    batch_size = 3000
    data_delay = 1  # sec default 10
    data_visualize = DataVisualize(batch_size=batch_size, data_size = data_size)
    data_visualize_2 = DataVisualize(batch_size = batch_size, data_size=data_size)

    client = create_client()
    cl_connection = create_connections(client)
    cl_batch = c104.Batch(cause=c104.Cot.SPONTANEOUS)
    cl_batch_2 = c104.Batch(cause=c104.Cot.SPONTANEOUS)
    # client = add_client_handlers(client)
    # cl_connection = add_connection_handlers(cl_connection)
    cl_station = cl_connection.add_station(common_address=46) # create station on client side
    server = create_server()
    # server = add_server_handlers(server)
    sv_station = server.add_station(common_address=47) # create station on server with adress 47
    sv_station_2 = server.add_station(common_address=48)
    sv_measure = create_measure(sv_station)
    sv_measure.on_receive(callable=cl_point_on_recieve)
    sv_batch = create_batch(sv_station, batch_size, start_io=100)
    sv_batch_2 = create_batch(sv_station_2, batch_size, start_io=100)

    print(cl_connection.stations, server.stations)
    data_visualize.batch_data = cl_batch
    data_visualize.connection = cl_connection
    data_visualize.generate_plot()
    data_visualize_2.batch_data = cl_batch_2
    data_visualize_2.connection = cl_connection
    data_visualize_2.generate_plot()
    server.start()
    client.start()

    while not cl_connection.is_connected or cl_connection.is_muted:
        print("CL] Try to connect to {0}:{1}".format(cl_connection.ip, cl_connection.port))
        cl_connection.connect()
        time.sleep(3)
    print("CONNECTED TO STATION")
    time.sleep(1)
    print(cl_connection.stations, server.stations)
    cl_connection.connect()
    cl_station = cl_connection.get_station(common_address=47)
    cl_station_2 = cl_connection.get_station(common_address=48)
    point = cl_station.get_point(io_address=11)
    point.on_receive(callable=cl_pt_on_receive_point)
    for point in sv_batch.points:
        cl_point = cl_station.get_point(io_address=point.io_address)
        if cl_point is None:
            cl_station.add_point(io_address=point.io_address, type=c104.Type.M_ME_NC_1, report_ms=0)
            cl_point = cl_station.get_point(io_address=point.io_address)
        # cl_point.on_receive(callable=cl_point_on_recieve)
        cl_batch.add_point(cl_point)

    for point in sv_batch_2.points:
        cl_point = cl_station_2.get_point(io_address=point.io_address)
        if cl_point is None:
            cl_station_2.add_point(io_address=point.io_address, type=c104.Type.M_ME_NC_1, report_ms=0)
            cl_point = cl_station_2.get_point(io_address=point.io_address)
        # cl_point.on_receive(callable=cl_point_on_recieve)
        cl_batch_2.add_point(cl_point)

     # measurement is updated on client side in 1000 ms
    # batch = c104.Batch(cause=c104.Cot.SPONTANEOUS, points=[sv_measure])
    # print(batch)
    print()
    while True:
        time.sleep(data_delay)
        print("start transmiting")
        for step in range(data_visualize.batch_count):
            for point in sv_batch.points:
                point.value = float(random.randint(-63, 64))
                point.transmit(cause=sv_batch.cot)
            data_visualize.update_data(step)
        print(cl_connection.stations, server.stations)
        print("visualize client")
        data_visualize.update_plot()
        # time.sleep(data_delay)

        for step in range(data_visualize_2.batch_count):
            for point in sv_batch_2.points:
                point.value = float(random.randint(-63, 64))
                point.transmit(cause=sv_batch_2.cot)
            data_visualize_2.update_data(step)
        print(cl_connection.stations, server.stations)
        print("visualize client")
        data_visualize_2.update_plot()
        pass
    client.stop()
    server.stop()

if __name__ == "__main__":
    main()
