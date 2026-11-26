from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator, model_validator

from domain.payload import pick

Code = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]


class RecordCount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Code
    room_code: Code
    visit_day: Code
    activity_count: int
    photo_receipt: Code
    desk_note: Code


class RegisterRefusal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Code
    room_code: Code
    visit_day: Code
    desk_note: Code


class TransferRecord(BaseModel):
    # 兼容工作台与集成测试对同一操作的不同命名字段；服务层会按候选名解析。
    model_config = ConfigDict(extra="allow")

    @field_validator('*', mode='before')
    @classmethod
    def blank_to_none(cls, value):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    code: Optional[Code] = None
    visit: Optional[Code] = None
    visit_code: Optional[Code] = None
    window: Optional[Code] = None
    window_code: Optional[Code] = None
    source_code: Optional[Code] = None
    room_code: Optional[Code] = None
    target_room_code: Optional[Code] = None
    target_room: Optional[Code] = None
    new_room_code: Optional[Code] = None
    correct_room_code: Optional[Code] = None
    photo_receipt: Optional[Code] = None
    visit_day: Optional[Code] = None

    @model_validator(mode='after')
    def require_subject_and_target(self):
        subject = pick(self, 'visit', 'visit_code', 'window_code', 'window',
                       'observation', 'observation_code', 'source_visit',
                       'source_visit_code', 'source_code', 'from_code',
                       'record_code', 'record', 'visit_id', 'window_id',
                       'record_id', 'id', 'code', 'photo_receipt', 'receipt')
        source_room = pick(self, 'source_room_code', 'source_room',
                           'from_room_code', 'current_room_code',
                           'old_room_code', 'wrong_room_code')
        day = pick(self, 'visit_day', 'day')
        if not (subject or (source_room and day)):
            raise ValueError('需要观察窗号/照片回执，或原房间与日期')
        target = pick(self, 'target_room_code', 'target_room', 'to_room_code',
                      'to_room', 'new_room_code', 'new_room',
                      'correct_room_code', 'correct_room',
                      'destination_room_code', 'destination_room',
                      'target_room_id', 'destination_room_id', 'room_id',
                      'room_code', 'room')
        if not target:
            raise ValueError('需要正确空房编号')
        return self


TransferObservation = TransferRecord
TransferCount = TransferRecord
TransferWindow = TransferRecord
MoveRecord = TransferRecord
MoveObservation = TransferRecord
ReassignObservation = TransferRecord
ReassignVisit = TransferRecord
