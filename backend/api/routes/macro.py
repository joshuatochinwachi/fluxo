

# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/macro')
# async def macro():

#     # logic
#     return {'agent':'macro','status':'ok'}




from fastapi import APIRouter
from tasks.agent_tasks import macro_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/macro')
async def macro():
    task = macro_task.delay() # adding the background worker
    # logic
    return {'agent':'macro ','task_id': task.id}

# fetching the results
@router.get('/macro/status/{task_id}')
async def get_macro_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
