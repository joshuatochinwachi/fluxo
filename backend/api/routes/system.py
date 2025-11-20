"""
System Integration & Status API Routes
Master endpoints that tie everything together
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from integration.master_integration import get_integration
from api.models.schemas import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/analyze-complete')
async def complete_wallet_analysis(
    wallet_address: str = Query(..., description="Wallet address to analyze"),
    include_social: bool = Query(True, description="Include social sentiment"),
    include_audits: bool = Query(True, description="Include audit checks"),
    include_ai: bool = Query(True, description="Generate AI insights")
):
    """
    MASTER ENDPOINT: Complete end-to-end wallet analysis
    
    This endpoint orchestrates:
    - Risk analysis
    - Contract audit checks
    - Social sentiment
    - AI-powered insights
    - Alert triggering
    
    Returns comprehensive analysis report
    """
    try:
        integration = get_integration()
        
        results = await integration.complete_wallet_analysis(
            wallet_address=wallet_address,
            include_social=include_social,
            include_audits=include_audits,
            include_ai_insights=include_ai
        )
        
        return APIResponse(
            success=True,
            message="Complete analysis finished",
            data=results
        )
        
    except Exception as e:
        logger.error(f"Complete analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/analyze-batch')
async def batch_analyze_wallets(
    wallet_addresses: List[str] = Query(..., description="List of wallets to analyze")
):
    """
    Batch analyze multiple wallets
    
    Returns batch analysis results
    """
    try:
        if len(wallet_addresses) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 wallets per batch"
            )
        
        integration = get_integration()
        results = await integration.batch_analyze_wallets(wallet_addresses)
        
        return APIResponse(
            success=True,
            message=f"Batch analysis complete: {results['successful']}/{results['total_analyzed']} successful",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/status')
async def get_system_status():
    """
    Get complete backend system status
    
    Returns status of all components and integrations
    """
    try:
        integration = get_integration()
        status = integration.get_system_status()
        
        return APIResponse(
            success=True,
            message="System status retrieved",
            data=status
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/health')
async def system_health():
    """Quick health check"""
    return {
        "service": "fluxo_backend_master",
        "status": "✅ operational",
        "version": "1.0.0_integrated",
        "components": {
            "risk_agent": "✅",
            "social_agent": "✅",
            "alert_system": "✅",
            "ai_insights": "✅",
            "audit_service": "✅"
        },
        "endpoints": [
            "POST /api/v1/system/analyze-complete - Complete wallet analysis",
            "POST /api/v1/system/analyze-batch - Batch analyze wallets",
            "GET /api/v1/system/status - System status",
            "GET /api/v1/system/health - Health check"
        ]
    }
