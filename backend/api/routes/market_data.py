
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/market_data')
# async def market_data():

#     # logic
#     return {'agent':'market_data','status':'ok'}



from fastapi import APIRouter
from tasks.agent_tasks import market_data_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/market_data')
async def market_data():
    task = market_data_task.delay() # adding the background worker
    # logic
    return {'agent':'market_data ','task_id': task.id}

# fetching the results
@router.get('/market_data/status/{task_id}')
async def get_market_data_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
