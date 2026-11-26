from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import visit_windows_service as service
from domain.visit_windows_model import visit_windows
from domain.visit_windows_schemas import RecordCount, RegisterRefusal

router = APIRouter()

@router.get('/visit_windows')
def list_visit_windows(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, visit_windows)


@router.post('/visit_windows/record-count')
def record_count(data: RecordCount, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.record_count(conn, user, data)
        record(conn, user, 'visit_windows.record_count')
        return output


@router.post('/visit_windows/register-refusal')
def register_refusal(data: RegisterRefusal, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.register_refusal(conn, user, data)
        record(conn, user, 'visit_windows.register_refusal')
        return output
