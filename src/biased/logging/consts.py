# The key call sites nest their structured context under
# (``log.info("event", extra=dict(data=dict(...)))``); the formatter lifts it
# to the top level of the event, so the fields render as first-class keys.
DATA_KEY = "data"

HANDLER_NAME = "console"
