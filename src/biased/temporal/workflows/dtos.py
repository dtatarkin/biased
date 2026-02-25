from pydantic import StrictStr

from biased.dtos.base import BaseDto


class EchoWorkflowArg(BaseDto):
    message: StrictStr


class EchoWorkflowResult(BaseDto):
    message: StrictStr
