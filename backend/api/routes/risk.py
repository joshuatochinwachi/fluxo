
"""
Risk Analysis API Routes
Endpoints for portfolio risk scoring and analysis
"""
from fastapi import APIRouter, HTTPException
import logging

from api.models.schemas import PortfolioInput, APIResponse
from agents.risk_agent import RiskAgent

logger = logging.getLogger(_name_)

router = APIRouter()

# Initialize Risk Agent
risk_agent = RiskAgent()


@router.post("/analyze")
async def analyze_portfolio_risk(portfolio: PortfolioInput):
    """
    Analyze portfolio risk for a given wallet address
    
    Request body:
    {
        "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "network": "mantle"
    }
    
    Returns risk score, level, factors, and recommendations
    """
    try:
        logger.info(f"Analyzing portfolio for {portfolio.wallet_address}")
        
        # Call Risk Agent
        risk_score = await risk_agent.analyze_portfolio(portfolio)
        
        return APIResponse(
            success=True,
            message="Risk analysis completed successfully",
            data=risk_score.dict()
        )
        
    except Exception as e:
        logger.error(f"Risk analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Risk analysis failed: {str(e)}"
        )


@router.get("/score/{wallet_address}")
async def get_risk_score(wallet_address: str, network: str = "mantle"):
    """
    Quick risk score lookup (GET endpoint)
    
    Usage: GET /api/risk/score/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
    """
    try:
        portfolio = PortfolioInput(
            wallet_address=wallet_address,
            network=network
        )
        
        risk_score = await risk_agent.analyze_portfolio(portfolio)
        
        return APIResponse(
            success=True,
            message="Risk score retrieved",
            data={
                "wallet": wallet_address,
                "score": risk_score.score,
                "level": risk_score.level.value,
                "timestamp": risk_score.timestamp.isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get risk score: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/thresholds")
async def get_risk_thresholds():
    """
    Get current risk calculation thresholds and weights
    Useful for understanding how risk scores are calculated
    """
    return APIResponse(
        success=True,
        message="Risk calculation parameters",
        data={
            "weights": {
                "concentration": risk_agent.weights["concentration"],
                "liquidity": risk_agent.weights["liquidity"],
                "volatility": risk_agent.weights["volatility"],
                "contract": risk_agent.weights["contract"]
            },
            "thresholds": risk_agent.thresholds,
            "risk_levels": {
                "low": "0-30",
                "medium": "30-50",
                "high": "50-70",
                "critical": "70-100"
            }
        }
    )


@router.get("/")
async def risk_agent_status():
    """
    Health check for Risk Agent
    """
    return {
        "agent": "risk",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": [
            "POST /analyze - Full portfolio risk analysis",
            "GET /score/{wallet} - Quick risk score",
            "GET /thresholds - Risk calculation parameters"
        ]
    }
