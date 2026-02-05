from collections import namedtuple

protocol_fieldnames = (
    "connection_timeout",
    "message_timeout",
    "confirm_interval",
    "keep_alive_interval",
)
PROTOCOL_CONFIG = namedtuple(typename="protocol_config",
                             field_names=protocol_fieldnames)

PROTOCOL_CONFIG.connection_timeout = 20
PROTOCOL_CONFIG.message_timeout = 20
PROTOCOL_CONFIG.confirm_interval = 10
PROTOCOL_CONFIG.keep_alive_interval = 20


SERVERS = [
    ("127.0.0.1", 2404, 10) # ip , port, max_connections
]
