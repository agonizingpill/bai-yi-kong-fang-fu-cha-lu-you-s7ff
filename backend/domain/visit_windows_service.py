from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.key_handoffs_model import key_handoffs


def record_count(conn, user, data):
    from domain.visit_rules import calendar_day, good_permit, unique_window
    room = get(conn, vacant_rooms, data.room_code, lock=True)
    day = calendar_day(data.visit_day)
    good_permit(room,day)
    unique_window(conn,visit_windows,room['code'],day)
    need(0 <= data.activity_count <= 999 and data.photo_receipt.startswith('PHOTO-'),
        '实见数与照片回执需要一同登记')
    return insert(conn, visit_windows, **(data.model_dump() | {'visit_day':day}), status='已观测')


def register_refusal(conn, user, data):
    from domain.visit_rules import calendar_day, unique_window
    room = get(conn, vacant_rooms, data.room_code, lock=True)
    day = calendar_day(data.visit_day)
    unique_window(conn,visit_windows,room['code'],day)
    row = insert(conn, visit_windows, **(data.model_dump() | {'visit_day':day}),
        activity_count=None,photo_receipt=None,status='拒入未观测')
    update(conn, vacant_rooms, room['code'], status='需重新授权')
    return row
