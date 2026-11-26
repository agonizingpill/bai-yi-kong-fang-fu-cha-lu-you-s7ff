from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.payload import pick
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.forecast_rules import ensure_active_forecast
from domain.key_handoffs_model import key_handoffs


def _proof_by_receipt(conn, receipt, room_code=None):
    query = select(visit_windows).where(visit_windows.c.photo_receipt == receipt)
    if room_code is not None:
        query = query.where(visit_windows.c.room_code == room_code)
    row = conn.execute(query).mappings().first()
    need(row is not None, '找不到该房间对应的照片回执')
    return dict(row)


def book_revisit(conn, user, data):
    from domain.visit_rules import good_permit
    fit = get(conn, return_forecasts, data.forecast)
    room = get(conn, vacant_rooms, fit['room_code'], lock=True)
    fit = ensure_active_forecast(conn, data.forecast, room_code=room['code'], lock=True)
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
    ensure_active_forecast(conn, delivery['forecast'], room_code=room['code'], lock=True)
    proof = get(conn, visit_windows, delivery['proof_visit'])
    need(proof['room_code'] == delivery['room_code'] and proof['status'] == '已观测'
         and bool(proof['photo_receipt']),
         '原照片回执已转往其他空房，请先更换为本房回执，并凭新签认估计复约后再领钥匙')
    return update(conn,key_handoffs,data.handoff,status='钥匙已交接')


def return_key(conn, user, data):
    # 已签出的钥匙按原交接单归还；不再因照片转记或估计失效改变原单。
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


def change_receipt(conn, user, data):
    """Replace the photo proof on an unissued booking with a same-room receipt.

    An optional newly signed forecast can be supplied at the same time, allowing
    an invalidated estimate and moved photo to be corrected on the original
    booking before key release.
    """
    handoff_code = pick(data, 'handoff', 'handoff_code', 'booking',
                        'booking_code', 'key_handoff', 'code', 'id')
    need(handoff_code, '需要指定要更换回执的复约单号')
    preview = get(conn, key_handoffs, handoff_code)
    room = get(conn, vacant_rooms, preview['room_code'], lock=True)
    delivery = get(conn, key_handoffs, handoff_code, lock=True)
    need(delivery['status'] == '已复约',
         '只有尚未签出钥匙的复约可以更换同房回执；已借出的钥匙按原单归还')

    proof_code = pick(data, 'proof_visit', 'proof', 'visit', 'visit_code',
                      'window_code', 'window', 'observation_code',
                      'source_code', 'proof_code')
    receipt = pick(data, 'photo_receipt', 'receipt')
    if proof_code:
        proof = get(conn, visit_windows, proof_code, lock=True)
    else:
        need(receipt, '需要提供同房观察窗号或照片回执')
        proof = _proof_by_receipt(conn, receipt, room_code=room['code'])

    need(proof['room_code'] == room['code'] and proof['status'] == '已观测'
         and proof['activity_count'] is not None and bool(proof['photo_receipt']),
         '需要更换为同一空房的已观测实见记录')
    need(receipt is None or receipt == proof['photo_receipt'],
         '照片回执与观察记录中的原回执不一致')

    forecast_code = pick(data, 'forecast', 'new_forecast')
    if forecast_code is None:
        current_forecast = get(conn, return_forecasts, delivery['forecast'])
        if current_forecast.get('status', '有效') == '已失效':
            replacements = conn.execute(
                select(return_forecasts)
                .where(return_forecasts.c.room_code == room['code'])
                .where(return_forecasts.c.target_day == delivery['visit_date'])
                .where(return_forecasts.c.status == '有效')
                .order_by(return_forecasts.c.code.desc())
            ).mappings().all()
            if len(replacements) == 1:
                forecast_code = replacements[0]['code']
    team_member = pick(data, 'team_member', 'member', 'holder')
    values = {'proof_visit': proof['code']}
    if team_member:
        values['team_member'] = team_member
    if forecast_code:
        from domain.visit_rules import good_permit
        forecast = ensure_active_forecast(conn, forecast_code,
                                          room_code=room['code'], lock=True)
        need(proof['visit_day'] < forecast['target_day'],
             '照片观察日必须早于新估计的拟复访日期')
        good_permit(room, forecast['target_day'])
        values.update(forecast=forecast['code'],
                      active_forecast=forecast['code'],
                      visit_date=forecast['target_day'],
                      permit_snapshot=room['permit_ref'],
                      key_tag=room['key_tag'])
    else:
        need(proof['visit_day'] < delivery['visit_date'],
             '照片观察日必须早于拟交接日期')

    return update(conn, key_handoffs, handoff_code, **values)


replace_proof = change_receipt
change_proof = change_receipt
update_proof = change_receipt
replace_receipt = change_receipt
update_receipt = change_receipt
exchange_receipt = change_receipt
revise_booking = change_receipt
revise_handoff = change_receipt
