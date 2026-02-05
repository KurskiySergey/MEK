import time

import numpy as np
from mek_types.server import MEKServer
from mek_types.client import MEKClient
from mek_types.batch import MEKBatch, StationsBatch
from config import SERVERS
from mek_types.visualizer import DataVisualize, MultiDataVisualize, MultiStationVisualizer
import c104
from handlers.server_handlers import sv_on_connect
from handlers.client_handlers import on_batch_recieve
import asyncio
from multiprocessing import Process

def print_info(client: MEKClient, server: MEKServer):
    if client is not None:
        print(client)
        print()

    if server is not None:
        print(server)
        print()

def configure_client_server(stations = 1):
    # create client and server
    client = MEKClient(client_address=123)
    server = MEKServer(*SERVERS[0])

    # add stations at server side
    for i in range(stations):
        server.add_station(common_address=255 + i)
    # add connections
    add_server = SERVERS[0]
    client.add_connection(add_server[0], add_server[1], init=c104.Init.ALL)
    # set protocols
    client.set_protocol_config()

    # add handlers if necessary
    server.on_connect(callable=sv_on_connect)

    return client, server

def signal_function(size, mean, std = 20, T = 1000):
    x = np.linspace(start=0, stop=size, num=size)
    i = 0
    f = np.zeros_like(x)
    while mean + i*T < size:
        f += 50 * np.exp(-(x-(mean + i*T))**2 / std)
        i += 1
    return f

def one_point_test():
    print("CONFIGURATION UPLOAD...")
    # create client and server
    client, server = configure_client_server()
    # run server and client
    server.start()
    client.start()

    # try connect to server
    client.reconnect_all()

    # check connections
    client.check_connections()
    print("ALL CONNECTED")
    # print_info(client, server)

    # create batch of points for server side
    sv_station = server.get_station(common_address=255)
    sv_batch = MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1, batch_count=1,
                        start_address=1)
    # add log_point
    log_point = sv_station.add_point(io_address=2, type=c104.Type.M_SP_NA_1, report_ms=0)
    cl_point = client.add_point(log_point)
    cl_point.on_receive(callable=on_batch_recieve)
    sv_batch.log_point = log_point

    # print(sv_batch)
    # print_info(client, server)
    client.reconnect_all()
    client.check_connections()


    print("CONFIGURATION DONE")
    # print(client)

    # set update functions
    print("UPDATE CIRCLE START")
    circle_count = 10
    while circle_count != 0:
        time.sleep(3)  # each 10 sec
        print("update data")
        sv_batch.update_batch()
        # print(client, server)
        print("transmit data")
        sv_batch.transmit()
        time.sleep(1)  # wait for update
        # print(client, server)
        circle_count -= 1

    client.stop()
    server.stop()

def optodata_transmit_test():
    client, server = configure_client_server()

    client.start()
    server.start()
    client.check_connections()
    # configuring client and server
    batch_count = 500 # len of optodata
    start_address = 2 # address 1 for log point
    d_visualizer = DataVisualize(batch_size=batch_count)
    d_visualizer.generate_plot()

    # add random optodata on station
    sv_station = server.get_station(common_address=255)
    sv_batch = MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1,
                        batch_count=batch_count,
                        start_address=start_address,
                        delay_transmit=0)

    # add log_point
    log_point = sv_station.add_point(io_address=1, type=c104.Type.M_SP_NA_1, report_ms=0)
    cl_point = client.add_point(log_point)
    cl_point.on_receive(callable=on_batch_recieve)
    sv_batch.log_point = log_point
    # update client
    client.check_connections()
    cl_batch = client.batch_from_sv_batch(sv_batch)
    d_visualizer.monitor_batch = cl_batch

    print("UPDATE CIRCLE START")
    circle_count = 20
    velocity = 1
    sleep_time = 0.1
    delay_time = 0.1
    count = 0
    while circle_count != 0:
        time.sleep(sleep_time)  # each 10 sec
        print("update data")
        sv_batch.update_batch()
        upd_data = signal_function(size = batch_count, mean=0 + velocity * count)
        sv_batch.set_values(upd_data)
        # print(client, server)
        print("transmit data")
        sv_batch.transmit()
        time.sleep(delay_time)
        print("visualize data")
        d_visualizer.update_data()
        d_visualizer.update_plot()
        time.sleep(delay_time)  # wait for update
        # print(client, server)
        circle_count -= 1
        count += 1


    client.stop()
    server.stop()
    d_visualizer.close_plot()

def optodata_multi_transmit_test():
    client, server = configure_client_server()

    client.start()
    server.start()
    client.check_connections()
    # configuring client and server
    batch_count = 500
    data_size = 7000# len of optodata
    start_address = 2  # address 1 for log point
    md_visualizer = MultiDataVisualize(batch_size=batch_count, data_size=data_size)
    md_visualizer.generate_plot()

    # add random optodata on station
    sv_station = server.get_station(common_address=255)
    sv_batch = MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1,
                        batch_count=batch_count,
                        start_address=start_address,
                        delay_transmit=0)

    # add log_point
    log_point = sv_station.add_point(io_address=1, type=c104.Type.M_SP_NA_1, report_ms=0)
    cl_point = client.add_point(log_point)
    cl_point.on_receive(callable=on_batch_recieve)
    sv_batch.log_point = log_point
    # update client
    client.check_connections()
    cl_batch = client.batch_from_sv_batch(sv_batch)
    # cl_batch.add_receive_handler(handler=)
    md_visualizer.monitor_batch = cl_batch

    print("UPDATE CIRCLE START")
    circle_count = 20
    velocity = 250
    sleep_time = 2
    delay_time = 0.1
    count = 0
    while circle_count != 0:
        time.sleep(sleep_time)  # each 10 sec
        print("update data")
        start_time = time.time()
        sv_batch.update_batch()
        upd_data = signal_function(size=data_size, mean=0 + velocity * count)
        for i in range(md_visualizer.batch_count):
            sv_batch.set_values(upd_data[i*batch_count:(i+1)*batch_count])
            # print(client, server)
            print("transmit data")
            sv_batch.transmit()
            time.sleep(delay_time)
            md_visualizer.update_data(i)
        print("visualize data")
        stop_time = time.time()
        print(f"Send in {stop_time - start_time} s")
        md_visualizer.update_plot()
        time.sleep(delay_time)  # wait for update
            # print(client, server)
        circle_count -= 1
        count += 1

    client.stop()
    server.stop()
    md_visualizer.close_plot()

def transmit_on_back_test():
    client, server = configure_client_server()

    client.start()
    server.start()
    client.check_connections()
    # configuring client and server
    batch_count = 8000
    data_size = 7000  # len of optodata
    start_address = 2  # address 1 for log point
    d_visualizer = DataVisualize(batch_size=batch_count)
    d_visualizer.generate_plot()

    sv_station = server.get_station(common_address=255)
    sv_batch = MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1,
                        batch_count=batch_count,
                        start_address=start_address,
                        delay_transmit=0.00005)

    # add log_point
    log_point = sv_station.add_point(io_address=1, type=c104.Type.M_SP_NA_1, report_ms=0)
    cl_point = client.add_point(log_point)
    cl_point.on_receive(callable=on_batch_recieve)
    sv_batch.log_point = log_point
    # update client
    client.check_connections()
    cl_batch = client.batch_from_sv_batch(sv_batch)
    d_visualizer.monitor_batch = cl_batch

    print("UPDATE CIRCLE START")
    circle_count = 20
    velocity = 500
    sleep_time = 0.1
    delay_time = 0.1
    count = 0
    while circle_count != 0:
        time.sleep(sleep_time)  # each 10 sec
        print("update data")
        start_time = time.time()
        # sv_batch.update_batch()
        upd_data = signal_function(size=batch_count, mean=0 + velocity * count, std = 20000)
        sv_batch.set_values(upd_data)
        # print(client, server)
        print("transmit data")
        sv_batch.transmit(on_respond=True)
        time.sleep(delay_time)
        print("visualize data")
        stop_time = time.time()
        print(f"Send in {stop_time - start_time}")
        d_visualizer.update_data()
        d_visualizer.update_plot()
        time.sleep(delay_time)  # wait for update
        # print(client, server)
        circle_count -= 1
        count += 1

    client.stop()
    server.stop()
    d_visualizer.close_plot()

def multi_transmit_on_back_test():
    stations = 8
    client, server = configure_client_server(stations=stations)

    # configuring client and server
    client.start()
    server.start()
    client.check_connections()
    # configuring client and server
    batch_count = 7000
    data_size = 7000  # len of optodata
    start_address = 2  # address 1 for log point
    d_visualizer = MultiStationVisualizer(batch_size=batch_count, stations=stations)
    d_visualizer.generate_plot()
    sv_stations = [server.get_station(common_address=255 + i) for i in range(stations)]
    sv_batches = [MEKBatch(station=sv_station, cause=c104.Cot.SPONTANEOUS, batch_type=c104.Type.M_ME_NC_1,
                        batch_count=batch_count,
                        start_address=start_address,
                        delay_transmit=0.00005) for sv_station in sv_stations]

    station_batch = StationsBatch()
    station_batch.batches = sv_batches
    # add log_point
    use_log = False
    cl_batches = []
    for sv_station, sv_batch in zip(sv_stations, sv_batches):
        if use_log:
            log_point = sv_station.add_point(io_address=1, type=c104.Type.M_SP_NA_1, report_ms=0)
            cl_point = client.add_point(log_point)
            cl_point.on_receive(callable=on_batch_recieve)
            sv_batch.log_point = log_point
        cl_batch = client.batch_from_sv_batch(sv_batch)
        client.check_connections()
        cl_batches.append(cl_batch)
    d_visualizer.monitor_batch = cl_batches
    # update client


    print("UPDATE CIRCLE START")
    circle_count = 20
    velocity = 500
    sleep_time = 0.0
    delay_time = 0.3 # wait until update data
    count = 0
    while circle_count != 0:
        time.sleep(sleep_time)  # each 10 sec
        print("update data")
        start_time = time.time()
        # sv_batch.update_batch()
        upd_data = signal_function(size=batch_count, mean=0 + velocity * count, std = 20000)
        station_batch.set_values(upd_data)
        # print(client, server)
        print("transmit data")
        # asyncio.run(station_batch.async_transmit(on_respond=True))
        station_batch.transmit(on_respond=True)
        # station_batch.multiprocess_transmit(on_respond=True)
        before_delay_time = time.time()
        time.sleep(delay_time) # wait for update
        print("visualize data")
        stop_time = time.time()
        print(f"Send in {stop_time - start_time}, Before delay: {before_delay_time - start_time}")
        d_visualizer.update_data()
        d_visualizer.update_plot()
        # print(client, server)
        circle_count -= 1
        count += 1

    client.stop()
    server.stop()
    d_visualizer.close_plot()

if __name__ == "__main__":
    # one_point_test()
    # optodata_transmit_test()
    optodata_multi_transmit_test()
    # transmit_on_back_test()
    # multi_transmit_on_back_test()