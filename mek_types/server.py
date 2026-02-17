from config import PROTOCOL_CONFIG, SERVER_DIR
import c104
import os
import typing

class MEKServer(c104.Server):
    def __init__(self, ip: str = "0.0.0.0", port: int = 2404, max_connections: int = 0):
        super().__init__(ip=ip, port=port, max_connections=max_connections)
        self.__set_protocol_config()
        self.stations_batch = None
        self.meta_stations = None

    def save_data(self, filename, file_data: bytes):
        file_path = os.path.join(SERVER_DIR, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as w_file:
                w_file.write(file_data)
        else:
            print("filename already exists")

    def __set_protocol_config(self):
        self.protocol_parameters.message_timeout = PROTOCOL_CONFIG.message_timeout
        self.protocol_parameters.connection_timeout = PROTOCOL_CONFIG.connection_timeout
        self.protocol_parameters.keep_alive_interval = PROTOCOL_CONFIG.keep_alive_interval
        self.protocol_parameters.confirm_interval = PROTOCOL_CONFIG.confirm_interval
        # self.protocol_parameters.send_window_size = 1
        # self.protocol_parameters.receive_window_size = 1

    def get_point(self, io_address):
        sv_point = None
        find_point = False
        for station in self.stations:
            for point in station.points:
                if point.io_address == io_address:
                    sv_point = point
                    find_point = True
                    break
            if find_point:
                break

        return sv_point

    def __str__(self):
        res = super().__str__()
        print(res)
        print("-"*10 + "SERVER" + "-"*10)
        print(f"max connections: {self.max_connections}")
        print(f"current connections: {self.open_connection_count}")
        print("Station info")
        stations = self.stations
        print(f" {stations}")
        for station in stations:
            print(f"\tPoint info")
            points = station.points
            points_info = [(point, point.value) for point in points]
            print(f"\t {points_info}")



        return ""