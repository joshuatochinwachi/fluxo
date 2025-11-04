"""
Quick test script for Risk Agent
Run: python test_risk_agent.py
"""
import asyncio
from agents.risk_agent import RiskAgent
from api.models.schemas import PortfolioInput

async def test_risk_agent():
    # Initialize agent
    agent = RiskAgent()
    
    # Test portfolio
    portfolio = PortfolioInput(
        wallet_address="0x742d35cc6634c0532925a3b844bc9e7595f0beb",
        network="mantle"
    )
    
    # Run analysis
    result = await agent.analyze_portfolio(portfolio)
    
    # Print results
    print("=" * 50)
    print("RISK ANALYSIS RESULT")
    print("=" * 50)
    print(f"Overall Score: {result.score}/100")
    print(f"Risk Level: {result.level.value.upper()}")
    print("\nRisk Factors:")
    for factor, score in result.factors.items():
        print(f"  - {factor.capitalize()}: {score:.2f}")
    print("\nRecommendations:")
    for i, rec in enumerate(result.recommendations, 1):
        print(f"  {i}. {rec}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_risk_agent())
