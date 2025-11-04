
from fastapi import APIRouter

router = APIRouter()

@router.get('/social')
async def social():

    # logic
    return {'agent':'social','status':'ok'}