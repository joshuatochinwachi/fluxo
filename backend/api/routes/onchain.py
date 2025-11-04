
from fastapi import APIRouter

router = APIRouter()

@router.get('/onchain')
async def onchain():

    # logic
    return {'agent':'onchain freeman lilian','status':'ok'}