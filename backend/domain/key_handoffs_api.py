from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import key_handoffs_service as service
from domain.key_handoffs_model import key_handoffs
from domain.key_handoffs_schemas import BookRevisit, ReleaseKey, ReturnKey, CancelBooking

router = APIRouter()

@router.get('/key_handoffs')
def list_key_handoffs(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, key_handoffs)


@router.post('/key_handoffs/book-revisit')
def book_revisit(data: BookRevisit, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.book_revisit(conn, user, data)
        record(conn, user, 'key_handoffs.book_revisit')
        return output


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
