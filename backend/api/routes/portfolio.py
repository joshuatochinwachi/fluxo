from tasks.agent_tasks import portfolio_task
from celery.result import AsyncResult
from core import celery_app
from fastapi import APIRouter
from fastapi import APIRouter

router = APIRouter()

@router.get('/portfolio')
async def portfolio():

    # logic
    return {'agent':'portfolio','status':'ok'}



router = APIRouter()

@router.get('/portfolio')
async def portfolio():
    task = portfolio_task.delay() # adding the background worker
    # logic
    return {'agent':'portfolio ','task_id': task.id}

# fetching the results
@router.get('/portfolio/status/{task_id}')
async def get_portfolio_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }
