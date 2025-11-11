from fastapi import APIRouter, HTTPException
from tasks.agent_tasks import social_task
from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import APIResponse
from typing import Optional, List

router = APIRouter()

@router.post('/analyze')
async def analyze_sentiment(
    timeframe: str = "24h",
    focus_tokens: Optional[List[str]] = None
):
    """
    Start social sentiment analysis background task
    
    Query params:
    - timeframe: "1h", "24h", "7d" (default: "24h")
    - focus_tokens: Optional list of tokens to focus on
    
    Returns task_id to check progress
    """
    try:
        # Start background task
        task = social_task.delay(timeframe, focus_tokens)
        
        return APIResponse(
            success=True,
            message="Sentiment analysis started",
            data={
                "task_id": task.id,
                "status": "processing",
                "timeframe": timeframe,
                "check_status": f"/agent/social/status/{task.id}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get('/status/{task_id}')
async def get_social_status(task_id: str):
    """
    Get sentiment analysis task status and results
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.state.lower()
    }
    
    if task_result.state == 'PENDING':
        response_data['message'] = 'Task is queued'
        
    elif task_result.state == 'PROCESSING':
        info = task_result.info or {}
        response_data['progress'] = info.get('progress', 0)
        response_data['message'] = info.get('status', 'Processing...')
        
    elif task_result.state == 'SUCCESS':
        response_data['result'] = task_result.result
        response_data['message'] = 'Sentiment analysis completed'
        
    elif task_result.state == 'FAILURE':
        response_data['error'] = str(task_result.info)
        response_data['message'] = 'Analysis failed'
    
    return APIResponse(
        success=True,
        message="Task status retrieved",
        data=response_data
    )


@router.get('/social')
async def social_health():
    """Health check endpoint"""
    return {
        'agent': 'social',
        'status': 'operational',
        'endpoints': [
            'POST /agent/social/analyze - Start sentiment analysis',
            'GET /agent/social/status/{task_id} - Check task status'
        ]
    }
