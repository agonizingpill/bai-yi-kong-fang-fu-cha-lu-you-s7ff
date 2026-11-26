from typing import Annotated

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints

class RecordCount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    room_code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    visit_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    activity_count: int
    photo_receipt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    desk_note: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class RegisterRefusal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    room_code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    visit_day: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
    desk_note: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
