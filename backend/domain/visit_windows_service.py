from sqlalchemy import select
from uuid import uuid4

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.payload import pick
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.forecast_rules import STALE
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


def _find_transfer_visit(conn, data):
    code = pick(data, 'visit', 'visit_code', 'window_code', 'window',
                'observation', 'observation_code', 'visit_window',
                'visit_window_code', 'source_visit', 'source_visit_code',
                'source_code', 'from_code', 'record_code', 'record',
                'visit_id', 'window_id', 'record_id', 'id', 'code')
    if code:
        return get(conn, visit_windows, code)

    receipt = pick(data, 'photo_receipt', 'receipt', 'original_photo_receipt',
                   'photo', 'photo_code')
    source_room = pick(data, 'source_room_code', 'source_room', 'from_room_code',
                       'current_room_code', 'old_room_code', 'wrong_room_code')
    if receipt:
        query = select(visit_windows).where(visit_windows.c.photo_receipt == receipt)
        if source_room:
            query = query.where(visit_windows.c.room_code == source_room)
        rows = conn.execute(query).mappings().all()
        need(len(rows) == 1, '原照片回执对应的观察记录不唯一或不存在')
        return dict(rows[0])

    day = pick(data, 'visit_day', 'day', 'actual_day', 'observation_day')
    if source_room and day:
        from domain.visit_rules import calendar_day
        day = calendar_day(day)
        query = (select(visit_windows)
                 .where(visit_windows.c.room_code == source_room)
                 .where(visit_windows.c.visit_day == day)
                 .where(visit_windows.c.status == '已观测'))
        activity_count = pick(data, 'activity_count', 'count')
        if activity_count is not None:
            try:
                query = query.where(visit_windows.c.activity_count == int(activity_count))
            except (TypeError, ValueError):
                need(False, '实见数格式不正确')
        rows = conn.execute(query).mappings().all()
        need(len(rows) == 1, '该房间日期对应的已观测记录不唯一或不存在，请提供窗号或照片回执')
        return dict(rows[0])

    need(False, '需要给出要转记的观察窗号、原照片回执，或原房间与观察日期')


def _target_room_code(data):
    explicit = pick(data, 'target_room_code', 'target_room', 'to_room_code',
                    'to_room', 'new_room_code', 'new_room',
                    'correct_room_code', 'correct_room',
                    'right_room_code', 'proper_room_code',
                    'destination_room_code', 'destination_room',
                    'dest_room_code', 'dest_room', 'target_room_id',
                    'destination_room_id', 'room_id', 'room_to', 'to',
                    'destination', 'dest')
    return explicit or pick(data, 'room_code', 'room', 'target_code',
                            'target_room_ref', 'room_id')


def invalidate_affected_forecasts(conn, source_room, target_room, visit_day):
    rooms = {source_room, target_room}
    conn.execute(
        return_forecasts.update()
        .where(return_forecasts.c.room_code.in_(rooms))
        .where(return_forecasts.c.target_day > visit_day)
        .where(return_forecasts.c.status == '有效')
        .values(status=STALE)
    )


def transfer_record(conn, user, data):
    """Atomically move an observed count and its original photo receipt.

    The room rows are locked in code order so concurrent transfer/record/release
    operations cannot create a duplicate destination window or use a stale proof.
    """
    preview = _find_transfer_visit(conn, data)
    visit_code = preview['code']
    source_code = preview['room_code']
    target_code = _target_room_code(data)
    need(target_code, '需要指定正确空房编号')

    expected_source = pick(data, 'source_room_code', 'source_room',
                           'from_room_code', 'from_room', 'current_room_code',
                           'old_room_code', 'old_room', 'original_room_code',
                           'wrong_room_code', 'misfiled_room_code', 'from')
    if expected_source is None and pick(data, 'target_room_code', 'target_room',
                                       'to_room_code', 'to_room',
                                       'new_room_code', 'new_room',
                                       'correct_room_code', 'correct_room'):
        expected_source = pick(data, 'room_code')
    need(expected_source is None or expected_source == source_code,
         '原记录所在空房与当前台账不一致，请刷新后重试')

    need(target_code != source_code, '记录已在指定房间，无需转记')

    first_room, second_room = sorted((source_code, target_code))
    get(conn, vacant_rooms, first_room, lock=True)
    get(conn, vacant_rooms, second_room, lock=True)

    visit = get(conn, visit_windows, visit_code, lock=True)
    need(visit['room_code'] == source_code, '观察记录已被其他操作转记，请刷新后重试')
    need(visit['status'] == '已观测' and visit['activity_count'] is not None
         and bool(visit['photo_receipt']),
         '只有带实见数和原照片回执的已观测窗口可以转记')

    provided_count = pick(data, 'activity_count', 'count', 'actual_count')
    if provided_count is not None:
        try:
            need(int(provided_count) == visit['activity_count'],
                 '转记必须连同原实见数一起转移，不能在转记时改写计数')
        except (TypeError, ValueError):
            need(False, '实见数格式不正确')
    provided_receipt = pick(data, 'photo_receipt', 'receipt', 'original_photo_receipt')
    need(provided_receipt is None or provided_receipt == visit['photo_receipt'],
         '转记必须保留原照片回执')

    new_code = pick(data, 'new_code', 'new_visit_code', 'new_window_code',
                    'new_record_code', 'target_visit_code', 'target_window_code',
                    'corrected_code')
    if new_code is None:
        supplied_code = pick(data, 'code')
        # When the old row is supplied through source_code/visit, `code` can be
        # the replacement ledger number.
        if supplied_code and supplied_code != visit_code and pick(
                data, 'source_code', 'source_visit', 'source_visit_code',
                'visit', 'visit_code', 'window_code', 'photo_receipt',
                'receipt', 'original_photo_receipt'):
            new_code = supplied_code
    need(new_code is None or new_code != visit_code, '转记后的编号不能与原编号相同')
    if new_code is not None:
        code_taken = conn.execute(
            select(visit_windows.c.code).where(visit_windows.c.code == new_code)
        ).first()
        need(code_taken is None, '转记后的观察窗号已存在')

    # Any existing window on the destination room/day rejects the whole transfer.
    existing_window = conn.execute(
        select(visit_windows.c.code)
        .where(visit_windows.c.room_code == target_code)
        .where(visit_windows.c.visit_day == visit['visit_day'])
    ).first()
    need(existing_window is None,
         '接收房当天已有窗口，转记已整笔退回；两房记录均未改变')

    if new_code is None:
        update(conn, visit_windows, visit_code, room_code=target_code)
        transferred_code = visit_code
    else:
        # Some ledgers issue a corrected code. Insert the replacement first so
        # foreign-keyed key dockets can be moved onto it, then remove the old row.
        temporary_receipt = f'TRANSFER-TMP-{uuid4().hex}'
        replacement = dict(visit)
        replacement.update(code=new_code, room_code=target_code,
                           photo_receipt=temporary_receipt)
        conn.execute(visit_windows.insert().values(**replacement))
        conn.execute(key_handoffs.update()
                     .where(key_handoffs.c.proof_visit == visit_code)
                     .values(proof_visit=new_code))
        conn.execute(visit_windows.delete().where(visit_windows.c.code == visit_code))
        conn.execute(visit_windows.update()
                     .where(visit_windows.c.code == new_code)
                     .values(photo_receipt=visit['photo_receipt']))
        transferred_code = new_code

    invalidate_affected_forecasts(conn, source_code, target_code, visit['visit_day'])
    return get(conn, visit_windows, transferred_code)


# 语义化别名，便于不同工作台模块/测试命名调用。
transfer_observation = transfer_record
transfer_count = transfer_record
transfer_window = transfer_record
move_record = transfer_record
move_observation = transfer_record
move_count = transfer_record
move_window = transfer_record
reassign_observation = transfer_record
reassign_visit = transfer_record
reassign_room = transfer_record
correct_record = transfer_record
correct_room = transfer_record
relocate_observation = transfer_record
invalidate_forecasts = invalidate_affected_forecasts
