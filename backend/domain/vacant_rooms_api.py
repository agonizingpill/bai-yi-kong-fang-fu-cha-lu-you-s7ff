from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import vacant_rooms_service as service
from domain.vacant_rooms_model import vacant_rooms
from domain.vacant_rooms_schemas import RenewPermit

router = APIRouter()

@router.get('/vacant_rooms')
def list_vacant_rooms(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, vacant_rooms)


@router.post('/vacant_rooms/renew-permit')
def renew_permit(data: RenewPermit, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.renew_permit(conn, user, data)
        record(conn, user, 'vacant_rooms.renew_permit')
        return output
