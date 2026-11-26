from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class FitReturn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    target_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class SignReturn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    token: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
