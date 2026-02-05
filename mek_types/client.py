from config import PROTOCOL_CONFIG
from mek_types.batch import MEKBatch, StationsBatch
import c104
import time


class MEKClient(c104.Client):

    def __init__(self, client_address = 123):
        super().__init__()
        self.originator_address = client_address
        self.batches = StationsBatch()

    def set_protocol_config(self):
        for connection in self.connections:
            connection.protocol_parameters.connection_timeout = PROTOCOL_CONFIG.connection_timeout
            connection.protocol_parameters.message_timeout = PROTOCOL_CONFIG.message_timeout
            connection.protocol_parameters.confirm_interval = PROTOCOL_CONFIG.confirm_interval
            connection.protocol_parameters.keep_alive_interval = PROTOCOL_CONFIG.keep_alive_interval
            # connection.protocol_parameters.send_window_size = 1
            # connection.protocol_parameters.receive_window_size = 1

    def check_connections(self):
        for connection in self.connections:
            while not connection.is_connected or connection.is_muted:
                connection.connect()
                time.sleep(3)

    def add_point(self, point: c104.Point):
        point_station_address = point.station.common_address
        cl_point = None
        stop_adding = False
        for connection in self.connections:
            if not stop_adding:
                conn_stations = connection.stations
                for station in conn_stations:
                    if station.common_address == point_station_address:
                        cl_point = station.add_point(io_address=point.io_address,
                                                      type=point.type,
                                                      command_mode=point.command_mode,
                                                      report_ms=point.report_ms)
                        stop_adding = True
                        break

        return cl_point

    def batch_from_sv_batch(self, batch: MEKBatch):
        cl_batch = None
        stop_conn = False
        for connection in self.connections:
            if not stop_conn:
                stations = connection.stations
                for station in stations:
                    if station.common_address == batch.station.common_address:
                        cl_batch = MEKBatch.from_batch(batch, station)
                        stop_conn = True
                        break
        self.batches.add_batch(cl_batch)
        return cl_batch


    def __str__(self):
        res = super().__str__()
        print(res)
        print("-" * 10 + "CLIENT" + "-" * 10)
        print("total connections")
        print(self.connections)
        print("open connections count / active connections count")
        print(self.open_connection_count, self.active_connection_count)
        print("Station info")
        for connection in self.connections:
            print("Server ->", end=" ")
            print(connection.ip, connection.port)
            stations = connection.stations
            print(f" {stations}")
            print("\tPoint info")
            for station in stations:
                print(f"\tst address: {station.common_address}")
                points_info = [(point, point.value) for point in station.points]
                print(f"\t {points_info}")
        print("-" * 10 + "CLIENT END" + "-" * 10)
        return ""


