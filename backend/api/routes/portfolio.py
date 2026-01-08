"""
Portfolio API Routes
Combines Freeman's portfolio task + AI insights
"""
from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging

from celery.result import AsyncResult
from core import celery_app
from api.models.schemas import APIResponse, PortfolioInput
from services.ai_insights_engine import AIInsightsEngine
from api.models.schemas import APIResponse
from agents.risk_agent import RiskAgent
from agents.social_agent import SocialAgent
from agents.portfolio_agent import portfolio_agent

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/portfolio')
async def portfolio(address: str)->APIResponse:
    from tasks.agent_tasks.portfolio_task import fetch_portfolio
    # portf = portfolio_agent()
    # task =   await portf.retrieve_portfolio_data(address)
    task = fetch_portfolio.delay(address)
    # return {'data':'result'}
    return APIResponse(
        success=True,
        message=f'User Portfolio Data',
        data={
            'task_id':task.id,
            'check_status':f"/api/v1/agent/portfolio/status/{task.id}"
        }
    )


@router.get('/status/portfolio/{task_id}')
async def get_portfolio_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result,
    }


# ============= NEW AI INSIGHTS ENDPOINTS (ADD THESE) =============

@router.post('/insights')
async def generate_portfolio_insights(
    portfolio: PortfolioInput,
    include_social: bool = Query(True, description="Include social sentiment analysis"),
    include_macro: bool = Query(False, description="Include macro market analysis")
):
    """
    Generate AI-powered portfolio insights
    
    Request body:
    {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "network": "mantle"
    }
    
    Returns comprehensive AI-generated insights
    """
    try:
        logger.info(f"Generating insights for {portfolio.wallet_address}")
        
        # Initialize agents
        risk_agent = RiskAgent()
        ai_engine = AIInsightsEngine()
        
        # Get risk analysis
        risk_analysis = risk_agent.analyze_portfolio({
            "wallet": portfolio.wallet_address,
            "holdings": []
        })
        
        # Get social sentiment if requested
        social_sentiment = None
        if include_social:
            try:
                social_agent = SocialAgent(use_mock=False)
                social_sentiment = await social_agent.analyze_sentiment("MNT")
            except Exception as e:
                logger.warning(f"Social analysis failed: {str(e)}")
        
        # Generate AI insights
        insights = await ai_engine.generate_portfolio_insights(
            wallet_address=portfolio.wallet_address,
            risk_analysis=risk_analysis,
            social_sentiment=social_sentiment,
            macro_conditions=None
        )
        
        return APIResponse(
            success=True,
            message="Portfolio insights generated successfully",
            data=insights
        )
        
    except Exception as e:
        logger.error(f"Failed to generate insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/insights/quick')
async def quick_portfolio_insights(
    wallet_address: str = Query(..., description="Wallet address to analyze")
):
    """
    Quick portfolio insights (risk only, faster)
    """
    try:
        risk_agent = RiskAgent()
        ai_engine = AIInsightsEngine()
        
        risk_analysis = risk_agent.analyze_portfolio({
            "wallet": wallet_address,
            "holdings": []
        })
        
        insights = await ai_engine.generate_portfolio_insights(
            wallet_address=wallet_address,
            risk_analysis=risk_analysis,
            social_sentiment=None,
            macro_conditions=None
        )
        
        return APIResponse(
            success=True,
            message="Quick insights generated",
            data=insights
        )
        
    except Exception as e:
        logger.error(f"Quick insights failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/health')
async def portfolio_health():
    """Health check for portfolio service"""
    return {
        "service": "portfolio",
        "status": "operational",
        "version": "2.0_with_ai",
        "features": [
            "Portfolio task processing (Freeman)",
            "AI-powered insights (Muhammed)",
            "Multi-agent integration",
            "Quick insights mode"
        ],
        "endpoints": [
            "GET /agent/portfolio/portfolio - Start portfolio task",
            "GET /agent/portfolio/portfolio/status/{task_id} - Check task",
            "POST /agent/portfolio/insights - Full AI insights",
            "POST /agent/portfolio/insights/quick - Quick insights"
        ]
    }
