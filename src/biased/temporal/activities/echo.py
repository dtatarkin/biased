from datetime import timedelta

from temporalio import activity

from biased.temporal.activities.dtos import EchoActivityArg, EchoActivityResult
from biased.temporal.activities.utils import with_default_execute_params


@activity.defn(name="echo")
@with_default_execute_params(start_to_close_timeout=timedelta(seconds=3))
async def echo_activity(arg: EchoActivityArg) -> EchoActivityResult:
    return EchoActivityResult(message=arg.message)
