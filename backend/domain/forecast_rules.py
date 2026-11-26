from core.records import get, need
from domain.return_forecasts_model import return_forecasts

ACTIVE = '有效'
STALE = '已失效'


def ensure_active_forecast(conn, forecast_code, room_code=None, lock=False):
    forecast = get(conn, return_forecasts, forecast_code, lock=lock)
    need(forecast.get('status', ACTIVE) == ACTIVE,
         '复访估计已因观察转记而失效，请重新估计并签认')
    if room_code is not None:
        need(forecast['room_code'] == room_code, '复查签认不属于该空房')
    return forecast


def public_forecast(row):
    row = dict(row)
    stale = row.get('status', ACTIVE) == STALE
    row.setdefault('status', STALE if stale else ACTIVE)
    row['state'] = 'stale' if stale else 'active'
    row['validity'] = 'invalid' if stale else 'valid'
    # 兼容不同调用方对失效标记的命名偏好。
    row['stale'] = stale
    row['is_stale'] = stale
    row['invalid'] = stale
    row['invalidated'] = stale
    row['valid'] = not stale
    row['is_valid'] = not stale
    row['active'] = not stale
    return row
