
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/governance')
# async def governance():

#     # logic
#     return {'agent':'governance','status':'ok'}



from fastapi import APIRouter
from tasks.agent_tasks import governance_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/governance')
async def governance():
    task = governance_task.delay() # adding the background worker
    # logic
    return {'agent':'governance ','task_id': task.id}

# fetching the results
@router.get('/governance/status/{task_id}')
async def get_governance_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
