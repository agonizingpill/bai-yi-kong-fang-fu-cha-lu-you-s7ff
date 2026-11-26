from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class BookRevisit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    forecast: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    proof_visit: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    photo_receipt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    team_member: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class ReleaseKey(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    key_tag: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class ReturnKey(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    receipt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class CancelBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
