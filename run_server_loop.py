from handlers.server_handlers import sv_on_recieve_raw
from main import configure_client_server

if __name__ == "__main__":
    # start settings
    stations = 1  # optochannels count
    start_station_address = 255
    start_client_address = 123
    server_id = 0

    # get client and server
    client, server = configure_client_server(stations=stations, start_client_address=123, start_station_address=255,
                                             server_id=server_id)


    station = server.get_station(common_address=start_station_address)
    server.on_receive_raw(callable=sv_on_recieve_raw)
    print("START SERVER")
    server.start()
    print("SERVER RUNNING...")
    while True:
        ...