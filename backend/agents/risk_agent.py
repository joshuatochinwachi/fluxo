"""
Fluxo Risk Agent - Enhanced Portfolio Risk Scoring Engine
Analyzes concentration, liquidity, volatility, and contract risk

Week 2 Enhancement:
- Integrated Kelvin's Mantle protocol risk parameters
- Added correlation-based risk (from Kelvin's macro hypothesis)
- Improved liquidity scoring with real DEX data
- Enhanced contract risk with protocol safety scores
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)


class ProtocolRiskLevel(str, Enum):
    """Protocol safety classification based on Kelvin's research"""
    BLUE_CHIP = "blue_chip"      # Top tier (Uniswap, established)
    ESTABLISHED = "established"   # Well-known (Merchant Moe, FusionX)
    EMERGING = "emerging"         # Newer (Agni, TropicalSwap)
    UNVERIFIED = "unverified"     # Unknown/no audit


class PortfolioAsset(BaseModel):
    """Individual asset in portfolio"""
    token_symbol: str
    token_address: str
    balance: float
    usd_value: float
    percentage_of_portfolio: float
    protocol: Optional[str] = None  # Which protocol/DEX (if applicable)


class RiskMetrics(BaseModel):
    """Detailed risk breakdown"""
    concentration_score: float
    liquidity_score: float
    volatility_score: float
    contract_risk_score: float
    correlation_risk_score: float  # NEW: From Kelvin's hypothesis
    overall_score: float


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskScore(BaseModel):
    """Risk assessment output"""
    score: float
    level: RiskLevel
    factors: Dict[str, float]
    recommendations: List[str]
    market_condition: str  # NEW: Based on correlation
    timestamp: datetime


class RiskAgent:
    """
    Enhanced Risk Analysis Engine with Kelvin's Research
    
    Enhancements:
    1. Correlation-based market risk (Kelvin's macro hypothesis)
    2. Mantle protocol risk parameters (Kelvin's DEX data)
    3. Improved liquidity scoring
    4. Protocol safety classifications
    """
    
    def __init__(self):
        # Risk score weights (optimized based on Electus's feedback)
        self.weights = {
            "concentration": 0.30,   # Reduced slightly
            "liquidity": 0.25,
            "volatility": 0.20,
            "contract": 0.15,
            "correlation": 0.10      # NEW: Market correlation risk
        }
        
        # Kelvin's Mantle Protocol Safety Tiers
        self.protocol_tiers = {
            # Blue Chip - Highest safety
            "uniswap": ProtocolRiskLevel.BLUE_CHIP,
            
            # Established - Major Mantle DEXs (from Kelvin's data)
            "merchant_moe": ProtocolRiskLevel.ESTABLISHED,
            "fusionx": ProtocolRiskLevel.ESTABLISHED,
            "agni_finance": ProtocolRiskLevel.ESTABLISHED,
            
            # Emerging - Newer protocols
            "tropicalswap": ProtocolRiskLevel.EMERGING,
            "clipper_dex": ProtocolRiskLevel.EMERGING,
            "carbon_defi": ProtocolRiskLevel.EMERGING,
            "swaap": ProtocolRiskLevel.EMERGING,
        }
        
        # Protocol Risk Scores (0-100, lower = safer)
        self.protocol_risk_scores = {
            ProtocolRiskLevel.BLUE_CHIP: 5,
            ProtocolRiskLevel.ESTABLISHED: 15,
            ProtocolRiskLevel.EMERGING: 35,
            ProtocolRiskLevel.UNVERIFIED: 80
        }
        
        # Liquidity Tiers (from Kelvin's DEX data - TVL indicators)
        self.liquidity_tiers = {
            "merchant_moe": "high",      # Major Mantle DEX
            "fusionx": "high",           # Major Mantle DEX
            "uniswap": "very_high",      # Blue chip
            "agni_finance": "medium",
            "tropicalswap": "medium",
            "clipper_dex": "low",
            "carbon_defi": "low",
            "swaap": "medium"
        }
        
        # Correlation Risk Thresholds (from Kelvin's macro hypothesis)
        self.correlation_thresholds = {
            "healthy": 0.4,        # Below = healthy, selective market
            "neutral": 0.7,        # 0.4-0.7 = neutral/consolidating
            "stressed": 1.0        # Above 0.7 = fear/herd behavior
        }
        
        # Base thresholds
        self.thresholds = {
            "high_concentration": 40,      # % in single asset
            "very_high_concentration": 60, # Critical concentration
            "low_liquidity_usd": 100000,  # Below = high risk
            "high_volatility": 0.05,       # Daily 5% = high vol
            "min_diversification": 3       # Minimum # of assets
        }
    
    async def analyze_portfolio(
        self, 
        wallet_address: str,
        market_correlation: Optional[float] = None  # NEW: Pass from Macro Agent
    ) -> RiskScore:
        """
        Enhanced portfolio risk analysis
        
        Args:
            wallet_address: Wallet to analyze
            market_correlation: Current BTC/market correlation (0-1)
                               From Macro Agent based on Kelvin's hypothesis
        """
        try:
            # Fetch portfolio data
            assets = await self._fetch_portfolio_assets(wallet_address)
            
            if not assets:
                return self._create_empty_risk_score()
            
            # Calculate all risk metrics
            concentration = self._calculate_concentration(assets)
            liquidity = await self._calculate_liquidity(assets)
            volatility = await self._calculate_volatility(assets)
            contract_risk = await self._calculate_contract_risk(assets)
            
            # NEW: Correlation risk (from Kelvin's macro hypothesis)
            correlation_risk, market_condition = self._calculate_correlation_risk(
                market_correlation or 0.5  # Default to neutral if not provided
            )
            
            # Build metrics object
            metrics = RiskMetrics(
                concentration_score=concentration,
                liquidity_score=liquidity,
                volatility_score=volatility,
                contract_risk_score=contract_risk,
                correlation_risk_score=correlation_risk,
                overall_score=0  # Calculated next
            )
            
            # Compute weighted overall score
            overall_score = self._compute_overall_score(metrics)
            metrics.overall_score = overall_score
            
            # Determine risk level
            risk_level = self._get_risk_level(overall_score)
            
            # Generate recommendations (now includes correlation context)
            recommendations = self._generate_recommendations(
                metrics, 
                assets, 
                market_condition
            )
            
            # Build final risk score
            risk_score = RiskScore(
                score=overall_score,
                level=risk_level,
                factors={
                    "concentration": metrics.concentration_score,
                    "liquidity": metrics.liquidity_score,
                    "volatility": metrics.volatility_score,
                    "contract_risk": metrics.contract_risk_score,
                    "correlation_risk": metrics.correlation_risk_score
                },
                recommendations=recommendations,
                market_condition=market_condition,
                timestamp=datetime.utcnow()
            )
            
            logger.info(
                f"Risk analysis completed: {risk_level.value} ({overall_score:.1f}) "
                f"Market: {market_condition}"
            )
            return risk_score
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise
    
    async def _fetch_portfolio_assets(self, wallet_address: str) -> List[PortfolioAsset]:
        """
        Fetch portfolio with protocol information
        TODO Week 3: Real data from Freeman's data_pipeline
        """
<<<<<<< HEAD
        # Enhanced mock data with protocol info
=======

        """"
        Check service/dune_service.py for real implementation
        Checkout example.py for usage sample
        """
        # Mock portfolio for testing
>>>>>>> d2705d0 (Token Transfer Flow)
        mock_assets = [
            PortfolioAsset(
                token_symbol="mETH",
                token_address="0x...",
                balance=10.5,
                usd_value=35000,
                percentage_of_portfolio=70,
                protocol="merchant_moe"  # Staked on Merchant Moe
            ),
            PortfolioAsset(
                token_symbol="USDC",
                token_address="0x...",
                balance=10000,
                usd_value=10000,
                percentage_of_portfolio=20,
                protocol="fusionx"  # Liquidity on FusionX
            ),
            PortfolioAsset(
                token_symbol="MNT",
                token_address="0x...",
                balance=5000,
                usd_value=5000,
                percentage_of_portfolio=10,
                protocol=None  # Held in wallet
            )
        ]
        return mock_assets
    
    def _calculate_concentration(self, assets: List[PortfolioAsset]) -> float:
        """
        Enhanced concentration risk with diversification bonus
        Uses Herfindahl-Hirschman Index (HHI)
        """
        if not assets:
            return 0.0
        
        # HHI: Sum of squared market shares
        hhi = sum((asset.percentage_of_portfolio / 100) ** 2 for asset in assets)
        
        # Convert to 0-100 scale (1.0 = 100% in one asset = max risk)
        base_score = hhi * 100
        
        # Diversification bonus (Kelvin's input: min 3 assets is healthy)
        num_assets = len(assets)
        if num_assets >= 5:
            diversity_bonus = 10  # Well diversified
        elif num_assets >= 3:
            diversity_bonus = 5   # Acceptable
        else:
            diversity_bonus = 0   # Too concentrated
        
        concentration_score = max(0, base_score - diversity_bonus)
        
        logger.debug(
            f"Concentration: HHI={hhi:.3f}, Assets={num_assets}, "
            f"Score={concentration_score:.2f}"
        )
        return round(concentration_score, 2)
    
    async def _calculate_liquidity(self, assets: List[PortfolioAsset]) -> float:
        """
        Enhanced liquidity risk using Kelvin's DEX liquidity tiers
        """
        if not assets:
            return 0.0
        
        # Liquidity tier scores (0-100, lower = more liquid)
        tier_scores = {
            "very_high": 5,
            "high": 15,
            "medium": 35,
            "low": 60,
            "unknown": 75
        }
        
        weighted_liquidity = 0
        for asset in assets:
            # Get protocol liquidity tier
            protocol = asset.protocol
            if protocol and protocol.lower() in self.liquidity_tiers:
                tier = self.liquidity_tiers[protocol.lower()]
                asset_liquidity_score = tier_scores.get(tier, 75)
            else:
                # No protocol info or unknown protocol
                if asset.usd_value > self.thresholds["low_liquidity_usd"]:
                    asset_liquidity_score = 40  # Assume decent if large holding
                else:
                    asset_liquidity_score = 70  # Small + unknown = risky
            
            # Weight by portfolio percentage
            weight = asset.percentage_of_portfolio / 100
            weighted_liquidity += asset_liquidity_score * weight
        
        logger.debug(f"Liquidity risk score: {weighted_liquidity:.2f}")
        return round(weighted_liquidity, 2)
    
    async def _calculate_volatility(self, assets: List[PortfolioAsset]) -> float:
        """
        Enhanced volatility calculation
        TODO Week 3: Use actual historical price data
        """
        # Asset type volatility profiles (0-100 scale)
        volatility_profiles = {
            # Stablecoins - very low vol
            "USDC": 3,
            "USDT": 3,
            "DAI": 5,
            "FRAX": 8,
            
            # Blue chips - low to moderate
            "BTC": 30,
            "ETH": 35,
            "WETH": 35,
            
            # L2 tokens - moderate
            "mETH": 40,
            "MNT": 55,
            "OP": 50,
            "ARB": 50,
            
            # DeFi tokens - higher
            "MOE": 65,    # Merchant Moe token
            "FUSION": 65, # FusionX token
            
            # Unknown - assume high
            "UNKNOWN": 70
        }
        
        weighted_vol = 0
        for asset in assets:
            vol_score = volatility_profiles.get(
                asset.token_symbol.upper(), 
                volatility_profiles["UNKNOWN"]
            )
            weight = asset.percentage_of_portfolio / 100
            weighted_vol += vol_score * weight
        
        logger.debug(f"Volatility score: {weighted_vol:.2f}")
        return round(weighted_vol, 2)
    
    async def _calculate_contract_risk(self, assets: List[PortfolioAsset]) -> float:
        """
        Enhanced contract risk using Kelvin's protocol tiers
        """
        if not assets:
            return 0.0
        
        weighted_contract_risk = 0
        
        for asset in assets:
            # Determine protocol tier
            protocol = asset.protocol
            if protocol and protocol.lower() in self.protocol_tiers:
                tier = self.protocol_tiers[protocol.lower()]
                asset_risk = self.protocol_risk_scores[tier]
            else:
                # Check if it's a known safe token (held in wallet)
                safe_tokens = ["USDC", "USDT", "DAI", "WETH", "mETH", "MNT", "BTC", "ETH"]
                if asset.token_symbol.upper() in safe_tokens:
                    asset_risk = 10  # Known token, low risk even without protocol
                else:
                    asset_risk = 80  # Unknown token + unknown protocol = high risk
            
            # Weight by portfolio percentage
            weight = asset.percentage_of_portfolio / 100
            weighted_contract_risk += asset_risk * weight
        
        logger.debug(f"Contract risk score: {weighted_contract_risk:.2f}")
        return round(weighted_contract_risk, 2)
    
    def _calculate_correlation_risk(
        self, 
        market_correlation: float
    ) -> Tuple[float, str]:
        """
        NEW: Calculate correlation risk based on Kelvin's macro hypothesis
        
        From Kelvin's research:
        - Correlation < 0.4: Healthy (capital rotating, selective)
        - Correlation 0.4-0.7: Neutral (consolidating)
        - Correlation > 0.7: Stressed (fear, herd behavior)
        
        Args:
            market_correlation: Current market correlation (0-1)
        
        Returns:
            (risk_score, market_condition)
        """
        if market_correlation < self.correlation_thresholds["healthy"]:
            # Healthy market - low correlation risk
            risk_score = 15
            condition = "healthy_rotation"
            
        elif market_correlation < self.correlation_thresholds["neutral"]:
            # Neutral market - moderate correlation risk
            risk_score = 40
            condition = "neutral_consolidation"
            
        else:
            # Stressed market - high correlation risk
            # Scale from 70-100 based on how extreme
            excess = (market_correlation - 0.7) / 0.3  # 0 to 1
            risk_score = 70 + (excess * 30)
            condition = "stressed_correlation"
        
        logger.debug(
            f"Correlation risk: {risk_score:.2f} "
            f"(correlation={market_correlation:.2f}, condition={condition})"
        )
        return round(risk_score, 2), condition
    
    def _compute_overall_score(self, metrics: RiskMetrics) -> float:
        """Weighted average of all risk factors"""
        score = (
            metrics.concentration_score * self.weights["concentration"] +
            metrics.liquidity_score * self.weights["liquidity"] +
            metrics.volatility_score * self.weights["volatility"] +
            metrics.contract_risk_score * self.weights["contract"] +
            metrics.correlation_risk_score * self.weights["correlation"]
        )
        return round(score, 2)
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
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
        metrics: RiskMetrics,
        assets: List[PortfolioAsset],
        market_condition: str
    ) -> List[str]:
        """
        Enhanced recommendations with market context
        """
        recommendations = []
        
        # Concentration recommendations
        if metrics.concentration_score > 60:
            top_asset = max(assets, key=lambda a: a.percentage_of_portfolio)
            recommendations.append(
                f"⚠ Critical concentration: {top_asset.token_symbol} is "
                f"{top_asset.percentage_of_portfolio:.1f}% of portfolio. "
                f"Immediately diversify into 3-5 different assets to reduce risk."
            )
        elif metrics.concentration_score > 40:
            recommendations.append(
                "⚡ Moderate concentration detected. Consider spreading holdings "
                "across more assets for better diversification."
            )
        
        # Liquidity recommendations (with protocol context)
        if metrics.liquidity_score > 60:
            low_liquidity_assets = [
                a for a in assets 
                if a.protocol and self.liquidity_tiers.get(a.protocol.lower()) in ["low", "medium"]
            ]
            if low_liquidity_assets:
                protocols = ", ".join(set(a.protocol for a in low_liquidity_assets if a.protocol))
                recommendations.append(
                    f"💧 Low liquidity exposure on: {protocols}. "
                    f"Consider moving to higher liquidity DEXs like Merchant Moe or FusionX."
                )
        
        # Volatility recommendations
        if metrics.volatility_score > 50:
            recommendations.append(
                "📉 High volatility exposure. Add stablecoin allocation (USDC/USDT) "
                "to buffer against sharp price movements."
            )
        
        # Contract risk recommendations (with protocol tiers)
        if metrics.contract_risk_score > 40:
            risky_protocols = [
                a.protocol for a in assets 
                if a.protocol and self.protocol_tiers.get(a.protocol.lower()) == ProtocolRiskLevel.EMERGING
            ]
            if risky_protocols:
                recommendations.append(
                    f"🔒 Exposure to emerging protocols: {', '.join(set(risky_protocols))}. "
                    f"Review audit status and consider established alternatives."
                )
        
        # NEW: Correlation-based recommendations (Kelvin's hypothesis)
        if market_condition == "stressed_correlation":
            recommendations.append(
                "🌊 Market shows high correlation (>0.7) - indicating fear/herd behavior. "
                "Consider reducing overall risk exposure or increasing stable asset allocation. "
                "High correlation periods often precede volatility."
            )
        elif market_condition == "healthy_rotation":
            recommendations.append(
                "✅ Healthy market conditions (low correlation <0.4). "
                "Capital is rotating selectively - good environment for strategic rebalancing."
            )
        
        # Default if all looks good
        if not recommendations:
            recommendations.append(
                "✅ Portfolio risk profile is healthy. Continue monitoring regularly. "
                f"Market conditions: {market_condition.replace('_', ' ').title()}."
            )
        
        return recommendations
    
    def _create_empty_risk_score(self) -> RiskScore:
        """Return empty state for wallets with no assets"""
        return RiskScore(
            score=0.0,
            level=RiskLevel.LOW,
            factors={},
            recommendations=["No assets detected in portfolio."],
            market_condition="unknown",
            timestamp=datetime.utcnow()
        )


# Test function with enhanced output
async def test_enhanced_risk_agent():
    """Test the enhanced risk agent"""
    agent = RiskAgent()
    
    print("=" * 80)
    print(" " * 25 + "ENHANCED RISK AGENT TEST")
    print(" " * 20 + "(With Kelvin's Research Data)")
    print("=" * 80)
    
    # Test different market correlation scenarios
    scenarios = [
        (0.3, "Healthy Market (Low Correlation)"),
        (0.5, "Neutral Market (Moderate Correlation)"),
        (0.8, "Stressed Market (High Correlation)")
    ]
    
    for correlation, scenario_name in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario_name}")
        print(f"Market Correlation: {correlation:.2f}")
        print("=" * 80)
        
        # Run analysis with different correlations
        result = await agent.analyze_portfolio(
            "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            market_correlation=correlation
        )
        
        print(f"\n📊 Overall Risk: {result.level.value.upper()} ({result.score:.2f}/100)")
        print(f"🌍 Market Condition: {result.market_condition.replace('_', ' ').title()}")
        
        print(f"\n📈 Risk Factor Breakdown:")
        for factor, score in result.factors.items():
            bars = "█" * int(score / 5)
            print(f"  {factor.title():20s} {score:5.1f} {bars}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "=" * 80)
    print("Protocol Safety Tiers (from Kelvin's research):")
    print("=" * 80)
    for protocol, tier in agent.protocol_tiers.items():
        risk_score = agent.protocol_risk_scores[tier]
        print(f"  {protocol.title():20s} → {tier.value.title():15s} (Risk: {risk_score}/100)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_risk_agent())
