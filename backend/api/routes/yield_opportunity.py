# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/yield')
# async def Yield():

#     # logic
#     return {'agent':'yield','status':'ok'}


from fastapi import APIRouter
from tasks.agent_tasks import yield_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/yield')
async def Yield():
    task = yield_task.delay() # adding the background worker
    # logic
    return {'agent':'yield ','task_id': task.id}

# fetching the results
@router.get('/yield/status/{task_id}')
async def get_yield_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
