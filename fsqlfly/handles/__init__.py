from . import api_handler
from . import terminal_handler
from . import crud_handler
from . import file_handler

all_handles = (api_handler.default_handlers + file_handler.default_handlers +
               terminal_handler.default_handlers + crud_handler.default_handlers)
