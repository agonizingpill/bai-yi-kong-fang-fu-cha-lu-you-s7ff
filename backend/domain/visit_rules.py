from datetime import date

from sqlalchemy import select
from core.records import need


def calendar_day(value):
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        need(False, "日期应为 YYYY-MM-DD")
    need(parsed.isoformat() == value, "日期应为 YYYY-MM-DD")
    return parsed.isoformat()


def good_permit(room, day):
    need(room["status"] == "已授权" and room["permit_until"] is not None
         and day <= room["permit_until"], "房主需要重新授权，或现有授权未覆盖访问日")


def unique_window(conn, table, room, day):
    found = conn.execute(select(table.c.code).where(table.c.room_code == room, table.c.visit_day == day)).first()
    need(found is None, "同一空房已经登记了该日窗口")
