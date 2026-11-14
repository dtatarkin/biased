import json

from biased.utils.default_json_encoder import DefaultJsonEncoder


def test_utf8_bytes_decode_to_text():
    assert json.dumps("é".encode(), cls=DefaultJsonEncoder) == '"\\u00e9"'


def test_non_utf8_bytes_do_not_raise():
    assert json.loads(json.dumps(b"a\xffb", cls=DefaultJsonEncoder)) == "a\\xffb"
