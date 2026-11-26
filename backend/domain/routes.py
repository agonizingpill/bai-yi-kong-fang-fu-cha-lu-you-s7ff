from domain.vacant_rooms_api import router as vacant_rooms
from domain.visit_windows_api import router as visit_windows
from domain.return_forecasts_api import router as return_forecasts
from domain.key_handoffs_api import router as key_handoffs

routers = (vacant_rooms, visit_windows, return_forecasts, key_handoffs,)
