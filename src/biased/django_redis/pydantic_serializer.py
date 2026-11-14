from django_redis.serializers.base import BaseSerializer
from pydantic import BaseModel


class PydanticSerializer(BaseSerializer):
    """A django-redis serializer for a cache alias that stores only pydantic models.

    Writing dumps the model's full JSON. Reading returns that JSON as raw bytes,
    not a model: a serializer cannot know which model a key holds, so the
    caller validates it with ``Model.model_validate_json(cache.get(key))``.

    Plain ints never reach a serializer — django-redis stores them as they are
    and reads them back as ``int``. Any other non-model value raises
    ``TypeError``.
    """

    def dumps(self, value: object) -> bytes:
        if not isinstance(value, BaseModel):
            msg = f"{type(self).__name__} serializes pydantic models only, got {type(value).__name__}"
            raise TypeError(msg)
        return value.model_dump_json().encode()

    def loads(self, value: bytes) -> bytes:
        return value
