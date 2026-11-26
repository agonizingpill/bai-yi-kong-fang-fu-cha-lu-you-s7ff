from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator, model_validator

from domain.payload import pick

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class BookRevisit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Code
    forecast: Code
    proof_visit: Code
    photo_receipt: Code
    team_member: Code


class ReleaseKey(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Code
    key_tag: Code


class ReturnKey(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Code
    receipt: Code


class CancelBooking(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Code


class ChangeReceipt(BaseModel):
    model_config = ConfigDict(extra="allow")

    @field_validator('*', mode='before')
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    handoff: Optional[Code] = None
    code: Optional[Code] = None
    booking: Optional[Code] = None
    proof_visit: Optional[Code] = None
    visit: Optional[Code] = None
    visit_code: Optional[Code] = None
    window_code: Optional[Code] = None
    photo_receipt: Optional[Code] = None
    receipt: Optional[Code] = None
    forecast: Optional[Code] = None
    new_forecast: Optional[Code] = None

    @model_validator(mode='after')
    def require_handoff_and_proof(self):
        handoff = pick(self, 'handoff', 'handoff_code', 'booking',
                       'booking_code', 'key_handoff', 'code', 'id')
        proof = pick(self, 'proof_visit', 'proof', 'visit', 'visit_code',
                     'window_code', 'observation_code', 'proof_code',
                     'photo_receipt', 'receipt')
        if not handoff:
            raise ValueError('需要复约/交接号')
        if not proof:
            raise ValueError('需要同房观察窗号或照片回执')
        return self


ReplaceReceipt = ChangeReceipt
ReplaceProof = ChangeReceipt
ChangeProof = ChangeReceipt
UpdateReceipt = ChangeReceipt
ExchangeReceipt = ChangeReceipt
ReviseBooking = ChangeReceipt
ReviseHandoff = ChangeReceipt
