import c104
import time
import datetime

def sv_on_clock_sync(server: c104.Server, ip: str, date_time: datetime.datetime) -> c104.ResponseState:
    print("->@| Time {0} from {1} | SERVER {2}:{3}".format(date_time, ip, server.ip, server.port))
    return c104.ResponseState.SUCCESS

def sv_on_connect(server: c104.Server, ip: str)->bool:
    print("<->| {0} | SERVER {1} : {2}".format(ip, server.ip, server.port))
    return ip == "127.0.0.1"

def server_test():
    server = c104.Server()
    server.add_station(common_address=2)
    print("Get station")
    station = server.get_station(common_address=2)
    print(station)
    server.on_clock_sync(callable=sv_on_clock_sync)
    server.on_connect(callable=sv_on_connect)
    print("Start server")
    start_time = time.time()
    server.start()
    server.stop()
    print(f"Server stopped in {time.time() - start_time} sec")


if __name__ == "__main__":
    server_test()