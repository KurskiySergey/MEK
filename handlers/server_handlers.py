import c104

def sv_on_connect(server:c104.Server,ip:str)->bool:
    print(f"TRY TO CONNECT ON SERVER {ip}")
    return True
