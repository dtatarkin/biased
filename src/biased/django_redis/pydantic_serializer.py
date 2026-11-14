from django_redis.serializers.base import BaseSerializer
from pydantic import BaseModel


class PydanticSerializer(BaseSerializer):
    """A django-redis serializer for a cache alias that stores only pydantic models.

    Writing dumps the model's full JSON. Reading returns that JSON as raw bytes,
    not a model: a serializer cannot know which model a key holds, so the
    caller validates it with ``Model.model_validate_json(cache.get(key))``.

    django-redis stores a plain ``int`` as it is, without this serializer,
    and reads back as ``int`` any stored value that parses as one — so a
    model whose JSON is a bare integer, such as a ``RootModel[int]``, comes
    back as ``int``, not bytes. Any other non-model value, ``bool`` included,
    raises ``TypeError``.
    """

    def dumps(self, value: object) -> bytes:
        if not isinstance(value, BaseModel):
            msg = f"{type(self).__name__} serializes pydantic models only, got {type(value).__name__}"
            raise TypeError(msg)
        return value.model_dump_json().encode()

    def loads(self, value: bytes) -> bytes:
        return value
