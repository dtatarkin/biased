from pydantic import BaseModel, ConfigDict


class BaseDto(BaseModel):
    # Extra fields are ignored, not forbidden: DTOs carry Temporal workflow
    # payloads and parsed external reports, where a field dropped from the
    # model must not fail a payload recorded before the drop.
    model_config = ConfigDict(
        frozen=True,
    )
