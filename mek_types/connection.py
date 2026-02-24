import c104
from handlers.client_handlers import on_recieve_raw, on_send_raw

class MEKConnection(c104.Connection):

    def on_receive_raw(self, call = None):
        if call is None:
            super().on_receive_raw(on_recieve_raw)
        else:
            def concat_func(connection:c104.Connection,data:bytes)->None:
                call(connection, data)
                on_recieve_raw(connection, data)
            super().on_receive_raw(concat_func)

    def on_send_raw(self, call=None):
        if call is None:
            super().on_send_raw(on_send_raw)
        else:
            def concat_func(connection:c104.Connection,data:bytes) -> None:
                call(connection, data)
                on_send_raw(connection, data)

            super().on_send_raw(concat_func)
