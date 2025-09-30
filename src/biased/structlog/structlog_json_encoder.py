from biased.utils.default_json_encoder import DefaultJsonEncoder
from structlog.processors import _json_fallback_handler


class StructlogJsonEncoder(DefaultJsonEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return _json_fallback_handler(o)
