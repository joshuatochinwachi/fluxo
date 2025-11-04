
from fastapi import APIRouter

router = APIRouter()

@router.get('/execution')
async def execution():

    # logic
    return {'agent':'execution','status':'ok'}