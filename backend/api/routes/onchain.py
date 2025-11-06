from fastapi import APIRouter
from tasks import onchain_task

from celery.result import AsyncResult
from core import celery_app

router = APIRouter()

@router.get('/onchain')
async def onchain():
    task = onchain_task.delay() # adding the background worker
    # logic
    return {'agent':'onchain ','task_id': task.id}

# fetching the results
@router.get('/onchain/status/{task_id}')
async def get_onchain_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
