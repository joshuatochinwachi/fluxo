
from fastapi import APIRouter
# from tasks import execution_task # TODO: create tasks

from celery.result import AsyncResult
from core import celery_app
from tasks.agent_tasks.execution_task import execution_task,simulate_trade_task,approve_token_spending_task

router = APIRouter()

@router.get('/')
async def execution():
    task = execution_task.delay() # adding the background worker
    # logic
    return {'agent':'execution ','task_id': task.id}



@router.post("/simulate-trade")
async def trade_simulation(amount: int,address:str):
    if amount <=0:
        return {"error":"Amount must be greater than zero"}
    
    if address =="" or not address.startswith("0x") or len(address)!=42:
        return {"error":"Invalid wallet address"}

    task = simulate_trade_task.delay(amount,address)

    return {"status": "Trade Simulation Started", "task_id": task.id}
   
@router.post("/approve-token")
async def approve_token(token_address: str, spender_address: str, amount: float|int):
    if token_address =="" or not token_address.startswith("0x") or len(token_address)!=42:
        return {"error":"Invalid token address"}
    
    if spender_address =="" or not spender_address.startswith("0x") or len(spender_address)!=42:
        return {"error":"Invalid spender address"}

    if amount <=0:
        return {"error":"Amount must be greater than zero"}

    task = approve_token_spending_task.delay(token_address,spender_address,amount)

    return {"status": "Approval Started", "task_id": task.id}


@router.get('/simulate-trade/status/{task_id}')
async def get_trade_simulation_result(task_id:str):
    task_result = AsyncResult(task_id, app=celery_app)

    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }

