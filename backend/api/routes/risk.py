<<<<<<< HEAD
from fastapi import APIRouter, HTTPException, Query
from tasks.agent_tasks.risk_task import risk_task
=======
from fastapi import APIRouter, HTTPException
from tasks.agent_tasks import risk_task
>>>>>>> d2705d0 (Token Transfer Flow)
from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import PortfolioInput, APIResponse
from typing import Optional

router = APIRouter()

@router.post('/analyze')
async def analyze_risk(
    portfolio: PortfolioInput,
    market_correlation: Optional[float] = Query(None, ge=0, le=1, description="Market correlation (0-1)")
):
    """
    Start enhanced risk analysis background task
    
    Request body:
    {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "network": "mantle"
    }
    
    Query param (optional):
    - market_correlation: Current market correlation (0-1) from Macro Agent
    
    Returns task_id to check progress
    """
    try:
        # Start background task with market correlation
        task = risk_task.delay(
            portfolio.wallet_address, 
            portfolio.network,
            market_correlation
        )
        
        return APIResponse(
            success=True,
            message="Enhanced risk analysis started",
            data={
                "task_id": task.id,
                "status": "processing",
                "wallet_address": portfolio.wallet_address,
                "market_correlation": market_correlation,
                "check_status": f"/agent/risk/status/{task.id}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get('/status/{task_id}')
async def get_risk_status(task_id: str):
    """
    Get risk analysis task status and results
    
    Returns enhanced results with market condition context
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.state.lower()
    }
    
    if task_result.state == 'PENDING':
        response_data['message'] = 'Task is queued and waiting to start'
        
    elif task_result.state == 'PROCESSING':
        info = task_result.info or {}
        response_data['progress'] = info.get('progress', 0)
        response_data['message'] = info.get('status', 'Processing...')
        
    elif task_result.state == 'SUCCESS':
        result = task_result.result
        response_data['result'] = result
        response_data['message'] = 'Risk analysis completed successfully'
        
        # Highlight market condition if present
        if 'market_condition' in result:
            response_data['market_condition'] = result['market_condition']
        
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
        'version': '2.0_enhanced',
        'features': [
            'Concentration risk with diversification bonus',
            'Liquidity scoring with Mantle DEX tiers',
            'Protocol safety classification',
            'Market correlation risk (Kelvin\'s hypothesis)',
            'Context-aware recommendations'
        ],
        'endpoints': [
            'POST /agent/risk/analyze - Start risk analysis',
            'GET /agent/risk/status/{task_id} - Check task status'
        ]
    }
