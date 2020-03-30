from . import api_handler
from . import terminal_handler
from . import crud_handler

all_handles = api_handler.default_handlers + terminal_handler.default_handlers + crud_handler.default_handlers
