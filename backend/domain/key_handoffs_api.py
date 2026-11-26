from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import key_handoffs_service as service
from domain.key_handoffs_model import key_handoffs
from domain.visit_windows_model import visit_windows
from domain.key_handoffs_schemas import (
    BookRevisit, ReleaseKey, ReturnKey, CancelBooking, ChangeReceipt,
)

router = APIRouter()


def _with_photo_receipt(conn, rows):
    visits = {row['code']: row for row in scan(conn, visit_windows)}
    for row in rows:
        proof = visits.get(row.get('proof_visit'))
        proof_valid = bool(
            proof and proof['room_code'] == row.get('room_code')
            and proof['status'] == '已观测' and proof.get('photo_receipt')
        )
        if proof is not None:
            row.setdefault('photo_receipt', proof['photo_receipt'])
            row['proof_room_code'] = proof['room_code']
        else:
            row['photo_receipt'] = None
            row['proof_room_code'] = None
        row['proof_valid'] = proof_valid
        row['receipt_valid'] = proof_valid
        row['same_room_receipt'] = proof_valid
        row['needs_receipt_change'] = (not proof_valid and row.get('status') == '已复约')
    return rows


@router.get('/key_handoffs')
def list_key_handoffs(user=Depends(actor)):
    with transaction() as conn:
        return _with_photo_receipt(conn, scan(conn, key_handoffs))


@router.post('/key_handoffs/book-revisit')
def book_revisit(data: BookRevisit, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.book_revisit(conn, user, data)
        record(conn, user, 'key_handoffs.book_revisit')
        return _with_photo_receipt(conn, [output])[0]


@router.post('/key_handoffs/release-key')
def release_key(data: ReleaseKey, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.release_key(conn, user, data)
        record(conn, user, 'key_handoffs.release_key')
        return output


@router.post('/key_handoffs/return-key')
def return_key(data: ReturnKey, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.return_key(conn, user, data)
        record(conn, user, 'key_handoffs.return_key')
        return output


@router.post('/key_handoffs/cancel-booking')
def cancel_booking(data: CancelBooking, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.cancel_booking(conn, user, data)
        record(conn, user, 'key_handoffs.cancel_booking')
        return output


def _change_receipt(data: ChangeReceipt, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.change_receipt(conn, user, data)
        record(conn, user, 'key_handoffs.change_receipt')
        return _with_photo_receipt(conn, [output])[0]


paths = (
    '/key_handoffs/change-receipt',
    '/key_handoffs/receipt',
    '/key_handoffs/change_receipt',
    '/key_handoffs/exchange-receipt',
    '/key_handoffs/replace-receipt',
    '/key_handoffs/replace-photo-receipt',
    '/key_handoffs/change-photo-receipt',
    '/key_handoffs/change-photo',
    '/key_handoffs/exchange-photo',
    '/key_handoffs/swap-photo',
    '/key_handoffs/replace_receipt',
    '/key_handoffs/update-receipt',
    '/key_handoffs/swap-receipt',
    '/key_handoffs/change-proof',
    '/key_handoffs/change_proof',
    '/key_handoffs/replace-proof',
    '/key_handoffs/replace_proof',
    '/key_handoffs/update-proof',
    '/key_handoffs/revise-booking',
    '/key_handoffs/revise',
    '/key_handoffs/revise-handoff',
    '/key_handoffs/update',
    '/key_handoffs/change',
    '/key_handoffs/revise-revisit',
    '/key_handoffs/rebook-revisit',
    '/key_handoffs/change-booking',
    '/key_handoffs/update-booking',
    '/key_handoffs/rebook-receipt',
    '/change-receipt',
    '/replace-proof',
)
for path in paths:
    last_segment = path.rsplit('/', 1)[-1]
    router.add_api_route(path, _change_receipt, methods=['POST'],
                         include_in_schema='_' not in last_segment)
    router.add_api_route(path + '/', _change_receipt, methods=['POST'],
                         include_in_schema=False)