from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.vacant_rooms_model import vacant_rooms
from domain.visit_windows_model import visit_windows
from domain.return_forecasts_model import return_forecasts
from domain.key_handoffs_model import key_handoffs


def fit_return(conn, user, data):
    from domain.visit_rules import calendar_day
    day = calendar_day(data.target_day)
    get(conn, vacant_rooms, data.room_code)
    windows = [row for row in scan(conn, visit_windows)
        if row['room_code'] == data.room_code and row['visit_day'] < day]
    observations = [row for row in windows if row['status'] == '已观测']
    need(len(observations) >= 12, '同房间前序实见少于 12 次，复查估计尚不可用')
    return submit(user, {'room_code':data.room_code,'target_day':day,
         'observations':observations,'skipped_refusals':len(windows)-len(observations)})


def sign_return(conn, user, data):
    run = result(user,data.token)
    inputs, metrics = run['input'], run['result']
    room = get(conn, vacant_rooms, inputs['room_code'], lock=True)
    live = [row for row in scan(conn,visit_windows) if row['room_code']==room['code']
        and row['visit_day'] < inputs['target_day']]
    observed = [row for row in live if row['status']=='已观测']
    need(observed == inputs['observations'] and len(live)-len(observed)==inputs['skipped_refusals'],
         '新观察或拒入改变历史，请重新估计')
    return insert(conn, return_forecasts, code=data.code,token=data.token,
        room_code=room['code'],target_day=inputs['target_day'],
        **{k:metrics[k] for k in ('prediction','lag_count','gap_days','holdout_mae','skipped_refusals')})
