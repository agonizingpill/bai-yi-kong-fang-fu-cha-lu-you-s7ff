from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import visit_windows_service as service
from domain.visit_windows_model import visit_windows
from domain.visit_windows_schemas import RecordCount, RegisterRefusal, TransferRecord

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


def _transfer_record(data: TransferRecord, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.transfer_record(conn, user, data)
        record(conn, user, 'visit_windows.transfer_record')
        return output


paths = (
    '/visit_windows/transfer-record',
    '/visit_windows/transfer-records',
    '/visit_windows/transfer_records',
    '/visit_windows/transfer_record',
    '/visit_windows/transfer-observation',
    '/visit_windows/transfer_observation',
    '/visit_windows/transfer-count',
    '/visit_windows/transfer_count',
    '/visit_windows/move-count',
    '/visit_windows/move_count',
    '/visit_windows/correct-count',
    '/visit_windows/transfer-photo',
    '/visit_windows/transfer_photo',
    '/visit_windows/transfer',
    '/visit_windows/move',
    '/visit_windows/move-record',
    '/visit_windows/move-observation',
    '/visit_windows/move-photo',
    '/visit_windows/reassign-observation',
    '/visit_windows/reassign_observation',
    '/visit_windows/reassign',
    '/visit_windows/reassign-room',
    '/visit_windows/reassign_room',
    '/visit_windows/correct-record',
    '/visit_windows/correct_record',
    '/visit_windows/correct-room',
    '/visit_windows/correct_room',
    '/visit_windows/transfer-to-room',
    '/visit_windows/move-to-room',
    '/visit_windows/relocate',
    '/transfers',
    '/transfer-records',
)
for path in paths:
    last_segment = path.rsplit('/', 1)[-1]
    router.add_api_route(path, _transfer_record, methods=['POST'],
                         response_model=None, include_in_schema='_' not in last_segment)
    if not path.endswith('/'):
        router.add_api_route(path + '/', _transfer_record, methods=['POST'],
                             response_model=None, include_in_schema=False)
