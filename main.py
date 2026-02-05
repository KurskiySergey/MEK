from config import SERVERS
from mek_types.server import MEKServer
from mek_types.client import MEKClient
from mek_types.batch import StationsBatch, MEKBatch
from handlers.server_handlers import sv_on_connect
from handlers.client_handlers import on_batch_recieve
from mek_types.visualizer import MultiStationVisualizer
import numpy as np
import c104
import time

def signal_function(size, mean, std = 20, T = 1000):
    x = np.linspace(start=0, stop=size, num=size)
    i = 0
    f = np.zeros_like(x)
    while mean + i*T < size:
        f += 50 * np.exp(-(x-(mean + i*T))**2 / std)
        i += 1
    return f


def configure_client_server(stations = 1, start_client_address=123, start_station_address=255, server_id = 0):
    # create client and server
    client = MEKClient(client_address=start_client_address)
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


def run_update_circle(station_batch, visualizer, delay_time, batch_count, circle_count, velocity, use_patches = False, no_transmit = False):
    count = 0
    while circle_count != 0:
        print("update data")
        start_time = time.time()
        # update test data
        upd_data = signal_function(size=batch_count, mean=0 + velocity * count, std=20000)

        # print(client, server)
        print("transmit data")
        ## Send data on client side
        # set values on server side
        if not no_transmit:
            if use_patches:
                for i in range(visualizer.batch_count):
                    station_batch.set_values(upd_data[i * batch_count:(i + 1) * batch_count])
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
    batch_count = 7000  # full size of optodata
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
    data_size = 1000  # None if no patches, patch size of optodata otherwise
    batch_count = 7000  # full size of optodata
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
    batch_count = 7000  # full size of optodata
    start_io_address = 2  # address 1 for log point
    report_ms = 3000 # ms for point to report

    # set visualizer (only on client side )
    d_visualizer = MultiStationVisualizer(batch_size=batch_count, stations=stations, figsize=(12, 8),
                                          data_size=data_size)
    d_visualizer.generate_plot()

    if use_point_config:
        client, server = set_point_config(client, server, batch_count=batch_count, start_io_address=start_io_address, report_ms=report_ms)
    else:
        cl_batches = client.batches
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

if __name__ == "__main__":
    # start settings
    stations = 8 # optochannels count
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
    client, server = no_patches_use_test(client, server)
    client, server = patches_use_test(client, server, use_point_config=False)
    client, server = simple_report_test(client, server, use_point_config=False)

    client.stop()
    server.stop()



