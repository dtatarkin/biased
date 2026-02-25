from pydantic import StrictStr

from biased.dtos.base import BaseDto


class EchoActivityArg(BaseDto):
    message: StrictStr


class EchoActivityResult(BaseDto):
    message: StrictStr
