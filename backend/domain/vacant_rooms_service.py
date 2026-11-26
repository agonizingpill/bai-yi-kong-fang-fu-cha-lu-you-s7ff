from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.key_handoffs_model import key_handoffs


def renew_permit(conn, user, data):
    from domain.visit_rules import calendar_day
    room = get(conn, vacant_rooms, data.room_code, lock=True)
    deadline = calendar_day(data.permit_until)
    need(data.permit_ref.startswith('AUTH-') and data.permit_ref != room['permit_ref'],
        '重新授权需新的 AUTH 书面凭证')
    need(len(data.witness) >= 3,'缺审核见证')
    refusals = [row['visit_day'] for row in scan(conn, visit_windows)
        if row['room_code'] == room['code'] and row['status'] == '拒入未观测']
    need(not refusals or deadline > max(refusals), '新授权至少应晚于最后一次拒入')
    return update(conn, vacant_rooms, data.room_code, permit_ref=data.permit_ref,
        permit_until=deadline, status='已授权')
