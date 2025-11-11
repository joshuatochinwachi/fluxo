
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/research')
# async def research():

#     # logic
#     return {'agent':'research','status':'ok'}


from fastapi import APIRouter
from tasks.agent_tasks import research_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/research')
async def research():
    task = research_task.delay() # adding the background worker
    # logic
    return {'agent':'research ','task_id': task.id}

# fetching the results
@router.get('/research/status/{task_id}')
async def get_research_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
