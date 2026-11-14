from json import JSONEncoder

from ninja.renderers import JSONRenderer
from ninja.responses import NinjaJSONEncoder

from biased.utils.default_json_encoder import DefaultJsonEncoder


class BiasedNinjaJsonEncoder(DefaultJsonEncoder, NinjaJSONEncoder):
    """`DefaultJsonEncoder` first, so API output matches what it stores and logs;
    types it does not know fall through to Ninja's and then Django's encoder."""


class BiasedNinjaJsonRenderer(JSONRenderer):
    encoder_class: type[JSONEncoder] = BiasedNinjaJsonEncoder
