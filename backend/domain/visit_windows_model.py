from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


visit_windows = Table('visit_windows', metadata,
    Column('code', String(64), primary_key=True),
    Column('room_code', String(160), ForeignKey('vacant_rooms.code'), nullable=False),
    Column('visit_day', String(160), nullable=False),
    Column('activity_count', Integer, nullable=True),
    Column('status', String(160), nullable=False),
    Column('photo_receipt', String(160), nullable=True, unique=True),
    Column('desk_note', String(160), nullable=False),
    CheckConstraint("(status='拒入未观测' AND activity_count IS NULL AND photo_receipt IS NULL) OR (status='已观测' AND activity_count >= 0 AND photo_receipt IS NOT NULL)"),
)
