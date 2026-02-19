import time

import c104
from handlers.file_handlers import server_file_receive_handler, server_file_send_handler

def sv_on_connect(server:c104.Server, ip:str)->bool:
    print(f"TRY TO CONNECT ON SERVER {ip}")
    return True

sv_on_connect.__annotations__ = {
    'server': c104.Server,
    'ip': str,
    'return': bool
}

def sv_on_set_command_receive(point:c104.Point,previous_info:c104.Information,message:c104.IncomingMessage)->c104.ResponseState:
    print("Receive set point command")
    print(f"Previous value = {previous_info.value}")
    print(f"Next value = {point.value}")
    return c104.ResponseState.SUCCESS

sv_on_set_command_receive.__annotations__ = {
    'point': c104.Point,
    'previous_info': c104.Information,
    'message': c104.IncomingMessage,
    'return': c104.ResponseState
}

def sv_on_send_raw(server: c104.Server, data: bytes)->None:
    print("<--| {1} [{0}] | SERVER {2}:{3}".format(data.hex(), c104.explain_bytes(apdu=data), server.ip, server.port))


def sv_on_recieve_raw(server:c104.Server,data:bytes)->None:
    explain_dict = c104.explain_bytes_dict(data)
    type = explain_dict.get("type")

    if isinstance(type, c104.Type):
        if c104.Type.F_FR_NA_1.value <= type.value <= c104.Type.F_DR_TA_1.value:
            print(data)
            server_file_receive_handler(server, type, explain_dict)

sv_on_recieve_raw.__annotations__ = {
    'server': c104.Server,
    'data': bytes,
    'return': None
}