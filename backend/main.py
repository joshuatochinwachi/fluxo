"""
Fluxo - AI Automation-as-a-Service for Web3 Intelligence
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

# Import Routes
from api import (
    automation_router,
    execution_router,
    governance_router,
    macro_router,
    market_data_router,
    onchain_router,
    portfolio_router,
    research_router,
    risk_router,
    x402_router,
    yield_router,
    social_router,
    alerts_router

)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Fluxo API",
    description="AI Automation-as-a-Service for Web3 Intelligence",
    version="0.1.0"
)


# Attach Al Agent Routes
app.include_router(automation_router,prefix='/agent')
app.include_router(execution_router,prefix='/agent')
app.include_router(governance_router,prefix='/agent')
app.include_router(macro_router,prefix='/agent')
app.include_router(market_data_router,prefix='/agent')
app.include_router(portfolio_router,prefix='/agent')
app.include_router(research_router,prefix='/agent')
app.include_router(risk_router,prefix='/agent')
app.include_router(x402_router,prefix='/agent')
app.include_router(onchain_router,prefix='/agent')
app.include_router(yield_router,prefix='/agent')
app.include_router(social_router,prefix='/agent')
app.include_router(alerts_router, prefix="/api/alerts", tags=["Alerts"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "success": True,
        "message": "Fluxo API is running",
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "status": "healthy"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
