from config import PROTOCOL_CONFIG
import c104
import typing

class MEKServer(c104.Server):
    def __init__(self, ip: str = "0.0.0.0", port: int = 2404, max_connections: int = 0):
        super().__init__(ip=ip, port=port, max_connections=max_connections)
        self.__set_protocol_config()
        self.stations_batch = None

    def __set_protocol_config(self):
        self.protocol_parameters.message_timeout = PROTOCOL_CONFIG.message_timeout
        self.protocol_parameters.connection_timeout = PROTOCOL_CONFIG.connection_timeout
        self.protocol_parameters.keep_alive_interval = PROTOCOL_CONFIG.keep_alive_interval
        self.protocol_parameters.confirm_interval = PROTOCOL_CONFIG.confirm_interval
        # self.protocol_parameters.send_window_size = 1
        # self.protocol_parameters.receive_window_size = 1

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