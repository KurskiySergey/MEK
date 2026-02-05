import c104

def on_batch_recieve(point:c104.Point,previous_info:c104.Information,message:c104.IncomingMessage)->c104.ResponseState:
    print(f"CLIENT RECIEVE BATCH {point}")
    return c104.ResponseState.SUCCESS
