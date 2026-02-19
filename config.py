from collections import namedtuple
import os

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
    ("10.10.17.105", 2404, 10) # ip , port, max_connections
]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

FILES_FOLDER = "files"
SERVER_FOLDER = "server_side"
CLIENT_FOLDER = "client_side"
FILES_DIR = os.path.join(BASE_DIR, FILES_FOLDER)
SERVER_DIR = os.path.join(FILES_DIR, SERVER_FOLDER)
CLIENT_DIR = os.path.join(FILES_DIR, CLIENT_FOLDER)

SEGMENT_SIZE = 230
SECTION_SIZE = 10000

