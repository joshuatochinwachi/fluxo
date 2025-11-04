
from fastapi import APIRouter

router = APIRouter()

@router.get('/market_data')
async def market_data():

    # logic
    return {'agent':'market_data','status':'ok'}