from . import api_handler
from . import terminal_handler

all_handles = api_handler.default_handlers + terminal_handler.default_handlers
