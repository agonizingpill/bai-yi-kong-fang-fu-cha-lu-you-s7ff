from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


return_forecasts = Table('return_forecasts', metadata,
    Column('code', String(64), primary_key=True),
    Column('room_code', String(160), ForeignKey('vacant_rooms.code'), nullable=False),
    Column('target_day', String(160), nullable=False),
    Column('prediction', Float, nullable=False),
    Column('lag_count', Integer, nullable=False),
    Column('gap_days', Integer, nullable=False),
    Column('holdout_mae', Float, nullable=False),
    Column('skipped_refusals', Integer, nullable=False),
    Column('token', String(64), nullable=False, unique=True),
    CheckConstraint('prediction >= 0'),
    CheckConstraint('gap_days >= 1'),
    CheckConstraint('lag_count >= 0'),
    CheckConstraint('skipped_refusals >= 0'),
)
