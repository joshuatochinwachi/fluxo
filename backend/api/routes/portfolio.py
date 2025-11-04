
from fastapi import APIRouter

router = APIRouter()

@router.get('/portfolio')
async def portfolio():

    # logic
    return {'agent':'portfolio','status':'ok'}