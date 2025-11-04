"""
Fluxo Risk Agent - Portfolio Risk Scoring Engine
Analyzes concentration, liquidity, volatility, and contract risk
"""
from typing import List, Dict
from datetime import datetime
import logging
from pydantic import BaseModel

from api.models.schemas import RiskScore, RiskLevel, PortfolioInput

logger = logging.getLogger(__name__)


class PortfolioAsset(BaseModel):
    """Individual asset in portfolio"""
    token_symbol: str
    token_address: str
    balance: float
    usd_value: float
    percentage_of_portfolio: float


class RiskAgent:
    """
    Core Risk Analysis Engine
    
    Calculates risk based on:
    1. Concentration (35% weight)
    2. Liquidity (25% weight)  
    3. Volatility (25% weight)
    4. Contract Risk (15% weight)
    """
    
    def __init__(self):
        # Risk score weights (must sum to 1.0)
        self.weights = {
            "concentration": 0.35,
            "liquidity": 0.25,
            "volatility": 0.25,
            "contract": 0.15
        }
        
        # Thresholds (will be refined with Electus/Kelvin input)
        self.thresholds = {
            "high_concentration": 40,  # % in single asset
            "low_liquidity": 1_000_000,  # Min liquidity in USD
            "high_volatility": 0.05,     # Daily price change %
        }
    
    async def analyze_portfolio(self, portfolio_input: PortfolioInput) -> RiskScore:
        """
        Main entry point - analyze portfolio and return risk score
        """
        try:
            logger.info(f"Starting risk analysis for {portfolio_input.wallet_address}")
            
            # Step 1: Fetch portfolio data (mock for now)
            assets = await self._fetch_portfolio_assets(portfolio_input.wallet_address)
            
            if not assets:
                return self._create_empty_risk_score()
            
            # Step 2: Calculate individual risk metrics
            concentration_score = self._calculate_concentration(assets)
            liquidity_score = await self._calculate_liquidity(assets)
            volatility_score = await self._calculate_volatility(assets)
            contract_risk_score = await self._calculate_contract_risk(assets)
            
            # Step 3: Compute overall weighted score
            overall_score = (
                concentration_score * self.weights["concentration"] +
                liquidity_score * self.weights["liquidity"] +
                volatility_score * self.weights["volatility"] +
                contract_risk_score * self.weights["contract"]
            )
            overall_score = round(overall_score, 2)
            
            # Step 4: Determine risk level
            risk_level = self._get_risk_level(overall_score)
            
            # Step 5: Generate recommendations
            recommendations = self._generate_recommendations(
                concentration_score, 
                liquidity_score,
                volatility_score,
                contract_risk_score,
                assets
            )
            
            # Build result
            risk_score = RiskScore(
                score=overall_score,
                level=risk_level,
                factors={
                    "concentration": concentration_score,
                    "liquidity": liquidity_score,
                    "volatility": volatility_score,
                    "contract_risk": contract_risk_score
                },
                recommendations=recommendations
            )
            
            logger.info(f"Risk analysis completed: {risk_level.value} ({overall_score:.1f})")
            return risk_score
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise
    
    async def _fetch_portfolio_assets(self, wallet_address: str) -> List[PortfolioAsset]:
        """
        Fetch user's portfolio from blockchain
        TODO: Integrate with Freeman's data_pipeline service
        Using MOCK DATA for Week 1
        """
        # Mock portfolio for testing
        mock_assets = [
            PortfolioAsset(
                token_symbol="mETH",
                token_address="0x1234...",
                balance=10.5,
                usd_value=35000,
                percentage_of_portfolio=70
            ),
            PortfolioAsset(
                token_symbol="USDC",
                token_address="0x5678...",
                balance=10000,
                usd_value=10000,
                percentage_of_portfolio=20
            ),
            PortfolioAsset(
                token_symbol="MNT",
                token_address="0x9abc...",
                balance=5000,
                usd_value=5000,
                percentage_of_portfolio=10
            )
        ]
        return mock_assets
    
    def _calculate_concentration(self, assets: List[PortfolioAsset]) -> float:
        """
        Calculate concentration risk using Herfindahl Index
        High concentration = High risk
        """
        if not assets:
            return 0.0
        
        # Sum of squared percentages
        herfindahl = sum(
            (asset.percentage_of_portfolio / 100) ** 2 
            for asset in assets
        )
        
        # Convert to 0-100 scale
        concentration_score = herfindahl * 100
        
        logger.debug(f"Concentration score: {concentration_score:.2f}")
        return round(concentration_score, 2)
    
    async def _calculate_liquidity(self, assets: List[PortfolioAsset]) -> float:
        """
        Calculate liquidity risk
        TODO: Fetch actual DEX liquidity data from services/mantle_api.py
        """
        # MOCK: Simple scoring based on portfolio size
        total_value = sum(asset.usd_value for asset in assets)
        
        if total_value > self.thresholds["low_liquidity"]:
            return 20.0  # Low risk
        elif total_value > 100_000:
            return 50.0  # Medium risk
        else:
            return 80.0  # High risk
    
    async def _calculate_volatility(self, assets: List[PortfolioAsset]) -> float:
        """
        Calculate volatility risk
        TODO: Fetch historical price data from services/data_pipeline.py
        """
        # MOCK: Assign volatility based on token type
        volatility_map = {
            "USDC": 5,   # Stablecoin - very low
            "USDT": 5,
            "mETH": 40,  # Moderate volatility
            "MNT": 60,   # Higher volatility
            "BTC": 35,
            "ETH": 40
        }
        
        # Calculate weighted average
        weighted_vol = sum(
            volatility_map.get(asset.token_symbol, 50) * 
            (asset.percentage_of_portfolio / 100)
            for asset in assets
        )
        
        return round(weighted_vol, 2)
    
    async def _calculate_contract_risk(self, assets: List[PortfolioAsset]) -> float:
        """
        Calculate smart contract risk
        TODO: Integrate audit scores, TVL, contract age from services/defi_llama.py
        """
        # MOCK: Assume well-known tokens are safer
        known_safe_tokens = ["USDC", "USDT", "mETH", "MNT", "BTC", "ETH"]
        
        risky_exposure = sum(
            asset.percentage_of_portfolio
            for asset in assets
            if asset.token_symbol not in known_safe_tokens
        )
        
        return round(risky_exposure, 2)
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level enum"""
        if score < 30:
            return RiskLevel.LOW
        elif score < 50:
            return RiskLevel.MEDIUM
        elif score < 70:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(
        self, 
        concentration: float,
        liquidity: float,
        volatility: float,
        contract_risk: float,
        assets: List[PortfolioAsset]
    ) -> List[str]:
        """Generate actionable recommendations based on risk factors"""
        recommendations = []
        
        # Concentration check
        if concentration > 60:
            top_asset = max(assets, key=lambda a: a.percentage_of_portfolio)
            recommendations.append(
                f"High concentration risk: {top_asset.token_symbol} represents "
                f"{top_asset.percentage_of_portfolio:.1f}% of your portfolio. "
                f"Consider diversifying into 3-5 different assets."
            )
        
        # Liquidity check
        if liquidity > 60:
            recommendations.append(
                "Some assets may have low liquidity. Consider moving to more "
                "liquid alternatives on Merchant Moe or FusionX DEXs."
            )
        
        # Volatility check
        if volatility > 50:
            recommendations.append(
                "Portfolio has high volatility exposure. Consider adding "
                "stablecoin allocation (USDC/USDT) to reduce risk."
            )
        
        # Contract risk check
        if contract_risk > 40:
            recommendations.append(
                "Significant exposure to unaudited or newer contracts detected. "
                "Review security audits before increasing allocation."
            )
        
        # Default message if portfolio is healthy
        if not recommendations:
            recommendations.append(
                "Portfolio risk profile is healthy. Continue monitoring regularly."
            )
        
        return recommendations
    
    def _create_empty_risk_score(self) -> RiskScore:
        """Return empty state for wallets with no assets"""
        return RiskScore(
            score=0.0,
            level=RiskLevel.LOW,
            factors={},
            recommendations=["No assets detected in portfolio."]
        )
