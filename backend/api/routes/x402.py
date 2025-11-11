

# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/x402')
# async def x402():

#     # logic
#     return {'agent':'x402','status':'ok'}


from fastapi import APIRouter
from tasks.agent_tasks import x402_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/x402')
async def x402():
    task = x402_task.delay() # adding the background worker
    # logic
    return {'agent':'x402 ','task_id': task.id}

# fetching the results
@router.get('/x402/status/{task_id}')
async def get_x402_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
