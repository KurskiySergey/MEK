import typing

from c104f.config import SERVERS, SERVER_DIR, CLIENT_DIR
from c104f.mek_types.server import MEKServer
from c104f.mek_types.client import MEKClient
from c104f.mek_types.batch import StationsBatch, MEKBatch
from c104f.handlers.server_handlers import sv_on_connect, sv_on_set_command_receive, sv_on_send_raw, sv_on_recieve_raw
from c104f.handlers.client_handlers import on_batch_recieve, on_recieve_raw
from c104f.mek_types.visualizer import MultiStationVisualizer, DataVisualize
import numpy as np
import c104
import time
from c104f.utils.functions import signal_function, triangle_signal, rect_signal, sin_function
from typing import get_type_hints
import json
import os

def configure_client_server(stations = 1, start_client_address=123, start_station_address=255, server_id = 0):
    # create client and server
    client = MEKClient(client_address=start_client_address)
    print(SERVERS)
    server = MEKServer(*SERVERS[server_id])

    # add stations at server side
    for i in range(stations):
        server.add_station(common_address=start_station_address + i)
    # add connections
    client.add_connection(server.ip, server.port, init=c104.Init.ALL)
    # set protocols
    client.set_protocol_config()

    # add handlers if necessary
    server.on_connect(callable=sv_on_connect)

    return client, server

def configure_client_server_id(stations = 1, start_client_address=123, start_station_address=255, server_id: tuple = ("127.0.0.1", 2404, 10)):
    # create client and server
    client = MEKClient(client_address=start_client_address)
    server = MEKServer(*server_id)

    # add stations at server side
    for i in range(stations):
        server.add_station(common_address=start_station_address + i)
    # add connections
    client.add_connection(server.ip, server.port, init=c104.Init.ALL)
    # set protocols
    client.set_protocol_config()

    # add handlers if necessary
    server.on_connect(callable=sv_on_connect)

    return client, server


def run_update_circle(station_batch: StationsBatch, visualizer, delay_time, batch_count, circle_count,
                      velocity, use_patches = False, no_transmit = False, meta_use = False,
                      server: MEKServer = None, sv_cm_io = None, client = None, cl_points = None, cl_circle = None):
    count = 0
    cl_count = 0
    print("run update circle")
    while circle_count != 0:
        print("update data")
        if cl_count == cl_circle:
            print("update display info")
            for point in cl_points:
                point.info = c104.ScaledCmd(target=c104.Int16(np.random.randint(0, client.meta_stations)),
                                            qualifier=c104.UInt7(0))
                point.transmit(cause=c104.Cot.ACTIVATION)
            cl_count = 0
        start_time = time.time()
        # update test data
        upd_data = [
            signal_function(size=batch_count, ampl=15, mean=0 + velocity * count, std=20000),
            triangle_signal(size=batch_count, ampl=25, mean=0 + velocity * count, width=200, T=500),
            rect_signal(size=batch_count, ampl=9, mean=0 + velocity * count, width=200, T=500),
            sin_function(size=batch_count, ampl=5, mean=0 + velocity * count, w=0.005)
        ]
        # compose rest signals as interference
        upd_data.append(1 / (upd_data[0] + 0.1))
        upd_data.append(upd_data[0] + upd_data[1])
        upd_data.append(1/(upd_data[3] + 0.1))
        upd_data.append(upd_data[3] - upd_data[2])
        upd_data = np.asarray(upd_data)

        if meta_use:
            sv_info_point = server.get_point(io_address=sv_cm_io)
            current_display = sv_info_point.value
            # print(current_display, type(int(current_display)))
            upd_data = np.expand_dims(upd_data[int(current_display)], axis=0)
            # print(upd_data)


        # print(client, server)
        print("transmit data")
        ## Send data on client side
        # set values on server side
        if not no_transmit:
            if use_patches:
                for i in range(visualizer.batch_count):
                    station_batch.set_values(upd_data[:,i * batch_count:(i + 1) * batch_count])
                    station_batch.transmit(on_respond=True)  # most quick
                    time.sleep(delay_time)  # wait for update
                    visualizer.update_data(step=i)
                before_delay_time = time.time()
            else:

                station_batch.set_values(upd_data)
                # asyncio.run(station_batch.async_transmit(on_respond=True))
                station_batch.transmit(on_respond=True) # most quick
                # station_batch.multiprocess_transmit(on_respond=True)

                before_delay_time = time.time()
                time.sleep(delay_time) # wait for update
                visualizer.update_data()
        else:
            station_batch.set_values(upd_data)
            before_delay_time = time.time()
            time.sleep(delay_time)  # wait for update
            visualizer.update_data()
        print("visualize data")
        stop_time = time.time()
        print(f"Send in {stop_time - start_time}, Before delay: {before_delay_time - start_time}")
        visualizer.update_plot()
        circle_count -= 1
        count += 1
        cl_count += 1

def set_point_config(client, server, batch_count, start_io_address, report_ms = 0):
    ####
    # SERVER -> STATION_1, STATION_2,  ...
    ## STATION_i -> POINT_1, .... , POINT_N -> each station represents each optochannel with batch_size length
    ###
    delay_transmit = 0.00005
    # get existing stations on server side
    sv_stations = [server.get_station(common_address=start_station_address + i) for i in range(stations)]
    # create batch of pointa on each station
    sv_batches = [MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1,
                           batch_count=batch_count,
                           start_address=start_io_address,
                           delay_transmit=delay_transmit,
                           report_ms=report_ms) for sv_station in sv_stations]

    # Unite data into single batch
    station_batch = StationsBatch()
    station_batch.batches = sv_batches
    server.stations_batch = station_batch

    # add log_point
    use_log = False
    cl_batches = []  # client side batches
    for sv_station, sv_batch in zip(sv_stations, sv_batches):
        if use_log:
            log_point = sv_station.add_point(io_address=start_io_address - 1, type=c104.Type.M_SP_NA_1, report_ms=0)
            # add log point to client and set handler
            cl_point = client.add_point(log_point)
            cl_point.on_receive(callable=on_batch_recieve)
            # sync with server
            sv_batch.log_point = log_point
        # sync server batch on client side
        cl_batch = client.batch_from_sv_batch(sv_batch)
        cl_batches.append(cl_batch)
    # check connections
    client.check_connections()

    return client, server

def no_patches_use_test(client, server, use_point_config = True):
    # configure random optodata
    data_size = None  # None if no patches
    batch_count = 1250  # full size of optodata
    start_io_address = 2  # address 1 for log point
    report_ms = 0 # report trime of each point
    # set visualizer (only on client side )
    d_visualizer = MultiStationVisualizer(batch_size=batch_count, stations=stations, figsize=(12, 8),
                                          data_size=data_size)
    d_visualizer.generate_plot()





    if use_point_config:
        # generate batches for each station
        client, server = set_point_config(client, server, batch_count=batch_count, start_io_address=start_io_address, report_ms=report_ms)

    # set what visualizer will be monitoring
    d_visualizer.monitor_batch = client.batches

    print("UPDATE CIRCLE START")
    circle_count = 10  # count of iterations
    velocity = 500  # for test function visualizer
    delay_time = 0.3  # wait time until update
    use_patches = False  # end all data at once or by patches
    run_update_circle(station_batch=server.stations_batch, visualizer=d_visualizer, circle_count=circle_count,
                      delay_time=delay_time, batch_count = batch_count, velocity=velocity, use_patches=use_patches)

    d_visualizer.close_plot()
    return client, server

def patches_use_test(client, server, use_point_config = True):
    # configure random optodata
    data_size = 500  # None if no patches, patch size of optodata otherwise
    batch_count = 1250  # full size of optodata
    start_io_address = 2  # address 1 for log point

    # set visualizer (only on client side )
    d_visualizer = MultiStationVisualizer(batch_size=batch_count, stations=stations, figsize=(12, 8),
                                          data_size=data_size)
    d_visualizer.generate_plot()


    if use_point_config:
        client, server = set_point_config(client, server, batch_count=batch_count, start_io_address=start_io_address)

    d_visualizer.monitor_batch = client.batches

    print("UPDATE CIRCLE START")
    circle_count = 10  # count of iterations
    velocity = 500  # for test function visualizer
    delay_time = 0.1  # wait time until update
    use_patches = True  # end all data at once or by patches
    run_update_circle(station_batch=server.stations_batch, visualizer=d_visualizer, circle_count=circle_count,
                      delay_time=delay_time, batch_count=batch_count, velocity=velocity, use_patches=use_patches)

    d_visualizer.close_plot()
    return client, server

def simple_report_test(client, server, use_point_config = True):
    # configure random optodata
    data_size = None  # None if no patches, patch size of optodata otherwise
    batch_count = 1250  # full size of optodata
    start_io_address = 2  # address 1 for log point
    report_ms = 3000 # ms for point to report

    # set visualizer (only on client side )
    d_visualizer = MultiStationVisualizer(batch_size=batch_count, stations=stations, figsize=(12, 8),
                                          data_size=data_size)
    d_visualizer.generate_plot()

    if use_point_config:
        client, server = set_point_config(client, server, batch_count=batch_count, start_io_address=start_io_address, report_ms=report_ms)
    else:
        server.stations_batch.set_report_ms(report_ms)
    d_visualizer.monitor_batch = client.batches
    print("UPDATE CIRCLE START")
    circle_count = 10  # count of iterations
    velocity = 500  # for test function visualizer
    delay_time = 5  # wait time until update
    use_patches = False  # end all data at once or by patches
    run_update_circle(station_batch=server.stations_batch, visualizer=d_visualizer, circle_count=circle_count,
                      delay_time=delay_time, batch_count=batch_count, velocity=velocity, use_patches=use_patches, no_transmit=True)

    d_visualizer.close_plot()

    return client, server

def only_one_station_transmit_test(client, server, use_point_config = True):
    # configure random optodata
    data_size = None  # None if no patches
    batch_count = 1250  # full size of optodata
    start_io_address = 2  # address 1 for log point
    report_ms = 0  # report trime of each point


    # set visualizer (only on client side )
    d_visualizer = DataVisualize(batch_size=batch_count, figsize=(12, 8))

    if use_point_config:
        # generate batches for each station
        client, server = set_point_config(client, server, batch_count=batch_count, start_io_address=start_io_address, report_ms=report_ms)

    # add set_command point to client
    cl_io_address = 9000
    cl_points = []
    for station in server.stations:
        sv_point = station.add_point(io_address=cl_io_address, type=c104.Type.C_SE_NB_1, command_mode=c104.CommandMode.SELECT_AND_EXECUTE)
        cl_points.append(client.add_point(sv_point))
        sv_point.on_receive(callable=sv_on_set_command_receive)

    print("UPDATE CIRCLE START")
    circle_count = 20  # count of iterations
    velocity = 500  # for test function visualizer
    delay_time = 0.3  # wait time until update
    use_patches = False  # end all data at once or by patches
    meta_use = True
    cl_circle_count = 5 # how often update display

    # set what visualizer will be monitoring
    d_visualizer.monitor_batch = client.batches
    d_visualizer.generate_plot()
    run_update_circle(station_batch=server.stations_batch, visualizer=d_visualizer, circle_count=circle_count,
                      delay_time=delay_time, batch_count=batch_count, velocity=velocity,
                      use_patches=use_patches, meta_use=meta_use, server=server, sv_cm_io=cl_io_address,
                      client = client, cl_points = cl_points, cl_circle = cl_circle_count)

    d_visualizer.close_plot()

    return client, server

def sv_points_report_test(server, points_number, start_point_ioa = 2, report_ms = None):
    sv_stations = server.stations
    sv_batches = [MEKBatch(station=sv_station, cause=c104.Cot.PERIODIC, batch_type=c104.Type.M_ME_NC_1,
                           batch_count=points_number,
                           start_address=start_point_ioa,
                           delay_transmit=0,
                           report_ms=report_ms) for sv_station in sv_stations]


def file_transfer_test(client, server):
    # generate test file for optodata on server side
    c104.set_debug_mode(c104.Debug.Server)
    client.check_connections()
    # add server and client handlers
    connection = client.get_connection(common_address=start_station_address)
    connection.on_receive_raw(callable=on_recieve_raw)
    
    station = server.get_station(common_address=255)
    server.on_receive_raw(callable=sv_on_recieve_raw)
    point = station.add_point(io_address=4000, type=c104.Type.C_SE_NB_1)
    point.transmit(c104.Cot.SPONTANEOUS)

    # asdu transmit test
    zero_point = station.add_point(io_address=0, type=c104.Type.F_SC_NA_1)
    directory = c104.DirectoryCall(nof=c104.Int16(0), nos=c104.UInt7(0), scq=c104.UInt7(1))
    zero_point.info = directory
    zero_point.transmit(cause=c104.Cot.REQUEST)



if __name__ == "__main__":
    # start settings
    stations = 16 # optochannels count
    start_station_address = 255
    start_client_address = 123
    server_id = 0

    # get client and server
    client, server = configure_client_server(stations=stations, start_client_address=123, start_station_address=255, server_id=server_id)
    # start client and server
    client.start()
    server.start()
    client.check_connections()

    # full data transmit examples
    # server.on_send_raw(sv_on_send_raw)
    # station = server.get_station(common_address=255)
    client, server = no_patches_use_test(client, server)
    client, server = patches_use_test(client, server, use_point_config=False) # no need to config if was configured in previous functions
    client, server = simple_report_test(client, server, use_point_config=False)


    client.stop()
    server.stop()

    del client, server

    stations = 1
    meta_stations = 8 # real existing channels
    # get client and server
    client, server = configure_client_server(stations=stations, start_client_address=123, start_station_address=255,
                                             server_id=server_id)
    # start client and server
    server.meta_stations = meta_stations
    client.meta_stations = meta_stations
    client.start()
    server.start()
    client.check_connections()
    client, server = only_one_station_transmit_test(client, server, use_point_config=True)

    client.stop()
    server.stop()
    del client, server

    stations = 1
    client, server = configure_client_server(stations=stations, start_client_address=123, start_station_address=255,
                                             server_id=server_id)
    client.start()
    server.start()
    file_transfer_test(client, server)
    server.stop()
    client.stop()

hints = get_type_hints(configure_client_server)