"""
Risk Analysis API Routes
Enhanced with audit integration
"""
from fastapi import APIRouter, HTTPException, Query
from tasks.agent_tasks.risk_task import risk_task
from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import PortfolioInput, APIResponse
from typing import Optional
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/analyze')
async def analyze_risk(
    wallet_address: str,
    market_correlation: Optional[float] = Query(None, ge=0, le=1, description="Market correlation (0-1)")
):
    """
    Start enhanced risk analysis background task
    
    Request body:
    {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "network": "mantle"
    }
    
    Returns task_id to check progress
    """
    try:
        task = risk_task.delay(
            wallet_address
        )
        
        return APIResponse(
            success=True,
            message="Enhanced risk analysis started",
            data={
                "task_id": task.id,
                "status": "processing",
                "wallet_address": wallet_address,
                "market_correlation": market_correlation,
                "check_status": f"/api/v1/agent/risk/status/{task.id}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start task: {str(e)}")


@router.get('/status/{task_id}')
async def get_risk_status(task_id: str):
    """Get risk analysis task status and results"""
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
        response_data['message'] = 'Risk analysis completed'
        
        if 'market_condition' in task_result.result:
            response_data['market_condition'] = task_result.result['market_condition']
        
    elif task_result.state == 'FAILURE':
        response_data['error'] = str(task_result.info)
        response_data['message'] = 'Analysis failed'
    
    return APIResponse(
        success=True,
        message="Task status retrieved",
        data=response_data
    )


@router.post('/audit-check')
async def check_contract_audits(portfolio: PortfolioInput):
    """
    Check contract audit status for portfolio holdings
    
    Returns audit information and contract risk assessment
    """
    try:
        from agents.risk_agent import RiskAgent
        
        agent = RiskAgent()
        
        # Mock holdings
        holdings = [
            {"protocol": "mantle", "token": "MNT", "value": 10000},
            {"protocol": "meth", "token": "mETH", "value": 5000},
            {"protocol": "merchantmoe", "token": "MOE", "value": 3000}
        ]
        
        audit_results = await agent.check_contract_risk_with_audits(holdings)
        
        return APIResponse(
            success=True,
            message="Contract audit check completed",
            data={
                "wallet_address": portfolio.wallet_address,
                "audit_results": audit_results,
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Audit check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/audits/{protocol}')
async def get_protocol_audit(protocol: str):
    """
    Get audit information for a specific protocol
    
    Returns detailed audit information
    """
    try:
        from services.audit_feed_service import get_audit_service
        
        audit_service = get_audit_service()
        audit_info = await audit_service.get_protocol_audit(protocol)
        
        return APIResponse(
            success=True,
            message=f"Audit information for {protocol}",
            data=audit_info
        )
        
    except Exception as e:
        logger.error(f"Failed to get audit info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/risk')
async def risk_health():
    """Health check endpoint"""
    return {
        'agent': 'risk',
        'status': 'operational',
        'version': '2.0_with_audits',
        'features': [
            'Concentration risk with diversification bonus',
            'Liquidity scoring with Mantle DEX tiers',
            'Protocol safety classification',
            'Market correlation risk',
            'Audit feed integration',
            'Contract security analysis',
            'Context-aware recommendations'
        ],
        'endpoints': [
            'POST /api/v1/agent/risk/analyze - Start risk analysis',
            'GET /api/v1/agent/risk/status/{task_id} - Check task status',
            'POST /api/v1/agent/risk/audit-check - Check audits',
            'GET /api/v1/agent/risk/audits/{protocol} - Get protocol audit'
        ]
    }
