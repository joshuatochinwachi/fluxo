
from fastapi import APIRouter

router = APIRouter()

@router.get('/risk')
async def risk():

    # logic
    return {'agent':'risk','status':'ok'}