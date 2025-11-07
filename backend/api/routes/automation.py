# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/automation')
# async def automation_route():

#     # logic
#     return {'agent':'automation','status':'ok'}



from fastapi import APIRouter
#from tasks import automation_task #TODO: create task first

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/automation')
async def automation_route():
    task = automation_task.delay() # adding the background worker
    # logic
    return {'agent':'automation ','task_id': task.id}

# fetching the results
@router.get('/automation/status/{task_id}')
async def get_automation_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
