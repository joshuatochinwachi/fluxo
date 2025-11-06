from fastapi import APIRouter, HTTPException
from tasks.agent_tasks.risk_tasks import risk_task
from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import PortfolioInput, APIResponse

router = APIRouter()

@router.post('/analyze')
async def analyze_risk(portfolio: PortfolioInput):
    """
    Start risk analysis background task
    
    Request body:
    {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "network": "mantle"
    }
    
    Returns task_id to check progress
    """
    try:
        # Start background task
        task = risk_task.delay(portfolio.wallet_address, portfolio.network)
        
        return APIResponse(
            success=True,
            message="Risk analysis started",
            data={
                "task_id": task.id,
                "status": "processing",
                "wallet_address": portfolio.wallet_address,
                "check_status": f"/agent/risk/status/{task.id}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get('/status/{task_id}')
async def get_risk_status(task_id: str):
    """
    Get risk analysis task status and results
    
    Returns:
    - PENDING: Task waiting to start
    - PROCESSING: Task running
    - SUCCESS: Task completed with results
    - FAILURE: Task failed with error
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.state.lower()
    }
    
    if task_result.state == 'PENDING':
        response_data['message'] = 'Task is queued and waiting to start'
        
    elif task_result.state == 'PROCESSING':
        # Get progress info if available
        info = task_result.info or {}
        response_data['progress'] = info.get('progress', 0)
        response_data['message'] = info.get('status', 'Processing...')
        
    elif task_result.state == 'SUCCESS':
        response_data['result'] = task_result.result
        response_data['message'] = 'Risk analysis completed successfully'
        
    elif task_result.state == 'FAILURE':
        response_data['error'] = str(task_result.info)
        response_data['message'] = 'Risk analysis failed'
    
    return APIResponse(
        success=True,
        message="Task status retrieved",
        data=response_data
    )


@router.get('/risk')
async def risk_health():
    """Health check endpoint"""
    return {
        'agent': 'risk',
        'status': 'operational',
        'endpoints': [
            'POST /agent/risk/analyze - Start risk analysis',
            'GET /agent/risk/status/{task_id} - Check task status'
        ]
    }
