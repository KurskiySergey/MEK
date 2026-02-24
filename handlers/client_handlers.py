import c104

def on_batch_recieve(point:c104.Point,previous_info:c104.Information,message:c104.IncomingMessage)->c104.ResponseState:
    print(f"CLIENT RECIEVE BATCH {point}")
    return c104.ResponseState.SUCCESS

def on_recieve_raw(connection:c104.Connection,data:bytes)->None:
    print(data)
    dt = c104.explain_bytes_dict(data)
    dt_type = dt.get("type")

    if dt_type == c104.Type.F_DR_TA_1:
        elements = dt.get('elements')
        bytes_el = elements.split(" ")
        print(bytes_el)
        nof = elements[:2]
        lof = elements[2:2+4]
        sof = elements[6:7]
        print(sof)
    print(c104.explain_bytes_dict(data))
    print(c104.explain_bytes(data))

def on_send_raw(connection:c104.Connection,data:bytes)->None:
    pass