from fastapi import APIRouter

router = APIRouter()

@router.get('/automation')
async def automation_route():

    # logic
    return {'agent':'automation','status':'ok'}