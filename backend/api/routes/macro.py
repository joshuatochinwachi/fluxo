

from fastapi import APIRouter

router = APIRouter()

@router.get('/macro')
async def macro():

    # logic
    return {'agent':'macro','status':'ok'}