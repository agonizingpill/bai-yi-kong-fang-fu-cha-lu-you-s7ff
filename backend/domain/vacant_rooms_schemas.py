from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class RenewPermit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    room_code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    permit_ref: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    permit_until: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    witness: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
