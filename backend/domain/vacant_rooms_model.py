from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


vacant_rooms = Table('vacant_rooms', metadata,
    Column('code', String(64), primary_key=True),
    Column('building', String(160), nullable=False),
    Column('room', String(160), nullable=False),
    Column('contact_ref', String(160), nullable=False),
    Column('key_tag', String(160), nullable=False, unique=True),
    Column('permit_ref', String(160), nullable=True),
    Column('permit_until', String(160), nullable=True),
    Column('status', String(160), nullable=False),
    CheckConstraint("status IN ('已授权','需重新授权')"),
)
