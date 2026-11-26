from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


key_handoffs = Table('key_handoffs', metadata,
    Column('code', String(64), primary_key=True),
    Column('room_code', String(160), ForeignKey('vacant_rooms.code'), nullable=False),
    Column('forecast', String(160), ForeignKey('return_forecasts.code'), nullable=False),
    Column('active_forecast', String(160), ForeignKey('return_forecasts.code'), nullable=True, unique=True),
    Column('proof_visit', String(160), ForeignKey('visit_windows.code'), nullable=False),
    Column('permit_snapshot', String(160), nullable=False),
    Column('visit_date', String(160), nullable=False),
    Column('key_tag', String(160), nullable=False),
    Column('team_member', String(160), nullable=False),
    Column('status', String(160), nullable=False),
    Column('receipt', String(160), nullable=True, unique=True),
    CheckConstraint("status IN ('已复约','钥匙已交接','已归还','已取消')"),
)
