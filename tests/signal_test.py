import time

import c104
from server_tests import sv_on_connect, sv_on_clock_sync

def get_client(server_connection_ip = "127.0.0.1", server_port = 2404):
    client = c104.Client()
    client.add_connection(ip=server_connection_ip, port=server_port, init=c104.Init.ALL)
    return client

def get_server():
    server = c104.Server(ip="127.0.0.1", port=2404)
    server.add_station(common_address=15)
    server.on_connect(callable=sv_on_connect)
    server.on_clock_sync(callable=sv_on_clock_sync)
    return server


if __name__ == "__main__":
    server = get_server()
    server.max_connections = 10
    client = get_client(server_connection_ip=server.ip, server_port=server.port)
    client.start()
    server.start()
    connection = client.get_connection(ip=server.ip)
    print(connection.protocol_parameters.connection_timeout)
    connection.add_station(common_address=15)
    print(connection)
    print(client.has_active_connections, client.has_open_connections, client.has_connections)
    while not connection.is_connected or connection.is_muted:
        print("CL] Try to connect to {0}:{1}".format(connection.ip, connection.port))
        connection.connect()
        time.sleep(3)
    print()
    print(client.has_active_connections, client.has_open_connections, client.has_connections)
    print(connection)
    print("TEST COMMAND")
    print(connection.test(common_address=15))
    print("CLOCK SYNC")
    print(connection.clock_sync(common_address=15))
    print(connection)
    client.disconnect_all()
    print(connection)
    client.stop()
    server.stop()

