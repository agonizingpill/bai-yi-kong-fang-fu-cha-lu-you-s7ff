from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.key_handoffs_model import key_handoffs


def book_revisit(conn, user, data):
    from domain.visit_rules import good_permit
    fit = get(conn, return_forecasts, data.forecast)
    room = get(conn, vacant_rooms, fit['room_code'], lock=True)
    good_permit(room,fit['target_day'])
    proof = get(conn, visit_windows, data.proof_visit)
    need(proof['room_code']==room['code'] and proof['status']=='已观测'
        and proof['visit_day']<fit['target_day'] and data.photo_receipt==proof['photo_receipt'],
        '需要同一空房较早已观测的真实照片回执')
    return insert(conn, key_handoffs, code=data.code, forecast=data.forecast, active_forecast=data.forecast, proof_visit=proof['code'],
        room_code=room['code'],permit_snapshot=room['permit_ref'],visit_date=fit['target_day'],
        key_tag=room['key_tag'],team_member=data.team_member,status='已复约',receipt=None)


def release_key(conn, user, data):
    from domain.visit_rules import good_permit
    delivery = get(conn,key_handoffs,data.handoff)
    room = get(conn,vacant_rooms,delivery['room_code'],lock=True)
    delivery = get(conn,key_handoffs,data.handoff,lock=True)
    need(delivery['status']=='已复约' and data.key_tag==delivery['key_tag'],'交接状态或实物钥匙牌不符')
    good_permit(room,delivery['visit_date'])
    need(room['permit_ref']==delivery['permit_snapshot'],'房主授权已更新，须取消旧交接并重新复约')
    return update(conn,key_handoffs,data.handoff,status='钥匙已交接')


def return_key(conn, user, data):
    row = get(conn,key_handoffs,data.handoff,lock=True)
    need(row['status']=='钥匙已交接','先签出钥匙再登记归还')
    need(data.receipt.startswith('KEYRET-'),'缺钥匙归还回单')
    return update(conn,key_handoffs,data.handoff,status='已归还',receipt=data.receipt,active_forecast=None)


def cancel_booking(conn, user, data):
    delivery = get(conn, key_handoffs, data.handoff)
    get(conn, vacant_rooms, delivery['room_code'], lock=True)
    delivery = get(conn, key_handoffs, data.handoff, lock=True)
    need(delivery['status'] == '已复约', '已发出的钥匙必须先归还')
    return update(conn, key_handoffs, data.handoff, status='已取消', active_forecast=None)
