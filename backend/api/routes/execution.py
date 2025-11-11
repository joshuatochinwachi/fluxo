
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/execution')
# async def execution():

#     # logic
#     return {'agent':'execution','status':'ok'}



from fastapi import APIRouter
# from tasks import execution_task # TODO: create tasks

from celery.result import AsyncResult
from core import celery_app
from tasks.agent_tasks import execution_task
router = APIRouter()

@router.get('/execution')
async def execution():
    task = execution_task.delay() # adding the background worker
    # logic
    return {'agent':'execution ','task_id': task.id}

# fetching the results
@router.get('/execution/status/{task_id}')
async def get_execution_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
