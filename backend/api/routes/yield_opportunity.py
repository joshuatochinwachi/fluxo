from fastapi import APIRouter

router = APIRouter()

@router.get('/yield')
async def Yield():

    # logic
    return {'agent':'yield','status':'ok'}