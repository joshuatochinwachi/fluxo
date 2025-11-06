
# from fastapi import APIRouter

# router = APIRouter()

# @router.get('/social')
# async def social():

#     # logic
#     return {'agent':'social','status':'ok'}


from fastapi import APIRouter
from tasks import social_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/social')
async def social():
    task = social_task.delay() # adding the background worker
    # logic
    return {'agent':'social ','task_id': task.id}

# fetching the results
@router.get('/social/status/{task_id}')
async def get_social_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
