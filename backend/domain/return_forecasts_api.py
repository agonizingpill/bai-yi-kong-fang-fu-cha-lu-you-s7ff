from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import return_forecasts_service as service
from domain.return_forecasts_model import return_forecasts
from domain.return_forecasts_schemas import FitReturn, SignReturn

router = APIRouter()

@router.get('/return_forecasts')
def list_return_forecasts(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, return_forecasts)


@router.post('/return_forecasts/fit-return')
def fit_return(data: FitReturn, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.fit_return(conn, user, data)
        record(conn, user, 'return_forecasts.fit_return')
        return output


@router.post('/return_forecasts/sign-return')
def sign_return(data: SignReturn, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.sign_return(conn, user, data)
        record(conn, user, 'return_forecasts.sign_return')
        return output
