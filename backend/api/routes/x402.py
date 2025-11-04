

from fastapi import APIRouter

router = APIRouter()

@router.get('/x402')
async def x402():

    # logic
    return {'agent':'x402','status':'ok'}