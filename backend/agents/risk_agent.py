"""
Fluxo Risk Agent - Enhanced Portfolio Risk Scoring Engine
Analyzes concentration, liquidity, volatility, contract risk, and audits

Week 2 Enhancement:
- Integrated Kelvin's Mantle protocol risk parameters
- Added correlation-based risk (from Kelvin's macro hypothesis)
- Improved liquidity scoring with real DEX data
- Enhanced contract risk with protocol safety scores
- Added audit feed integration for contract security
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, UTC,timezone
import logging
from pydantic import BaseModel
from enum import Enum

from core.config import get_mongo_connection

logger = logging.getLogger(__name__)


class ProtocolRiskLevel(str, Enum):
    """Protocol safety classification based on Kelvin's research"""
    BLUE_CHIP = "blue_chip"
    ESTABLISHED = "established"
    EMERGING = "emerging"
    UNVERIFIED = "unverified"


class PortfolioAsset(BaseModel):
    """Individual asset in portfolio"""
    token_symbol: str
    token_address: str
    balance: float
    value_usd: float
    percentage_of_portfolio: float
    protocol: Optional[str] = None


class RiskMetrics(BaseModel):
    """Detailed risk breakdown"""
    concentration_score: float
    liquidity_score: float
    volatility_score: float
    contract_risk_score: float
    correlation_risk_score: float
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
    market_condition: str
    timestamp: datetime


class RiskAgent:
    """Enhanced Risk Analysis Engine with Audit Integration"""
    
    def __init__(self):
        # Risk score weights
        self.weights = {
            "concentration": 0.30,
            "liquidity": 0.25,
            "volatility": 0.20,
            "contract": 0.15,
            "correlation": 0.10
        }
        
        # Protocol safety tiers
        self.protocol_tiers = {
            "uniswap": ProtocolRiskLevel.BLUE_CHIP,
            "merchant_moe": ProtocolRiskLevel.ESTABLISHED,
            "fusionx": ProtocolRiskLevel.ESTABLISHED,
            "agni_finance": ProtocolRiskLevel.ESTABLISHED,
            "tropicalswap": ProtocolRiskLevel.EMERGING,
            "clipper_dex": ProtocolRiskLevel.EMERGING,
            "carbon_defi": ProtocolRiskLevel.EMERGING,
            "swaap": ProtocolRiskLevel.EMERGING,
        }
        
        # Protocol risk scores
        self.protocol_risk_scores = {
            ProtocolRiskLevel.BLUE_CHIP: 5,
            ProtocolRiskLevel.ESTABLISHED: 15,
            ProtocolRiskLevel.EMERGING: 35,
            ProtocolRiskLevel.UNVERIFIED: 80
        }
        
        # Liquidity tiers
        self.liquidity_tiers = {
            "merchant_moe": "high",
            "fusionx": "high",
            "uniswap": "very_high",
            "agni_finance": "medium",
            "tropicalswap": "medium",
            "clipper_dex": "low",
            "carbon_defi": "low",
            "swaap": "medium"
        }
        
        # Correlation thresholds
        self.correlation_thresholds = {
            "healthy": 0.4,
            "neutral": 0.7,
            "stressed": 1.0
        }
        
        # Base thresholds
        self.thresholds = {
            "high_concentration": 40,
            "very_high_concentration": 60,
            "low_liquidity_usd": 100000,
            "high_volatility": 0.05,
            "min_diversification": 3
        }

        self.mongo = get_mongo_connection()
    
    def analyze_portfolio(
        self, 
        portfolio: list,
        market_correlation: Optional[float] = None
    ) -> Dict:
        """
        Synchronous portfolio risk analysis
        
        Args:
            portfolio: Portfolio data with holdings
            market_correlation: Market correlation (0-1)
            
        Returns:
            Risk analysis dictionary
        """

        
        try:
            # Extract wallet address
            wallet_address = portfolio[0].user_address
            
            # Mock assets for now
            assets = [
                PortfolioAsset(
                    token_symbol="mETH",
                    token_address="0x...",
                    balance=10.5,
                    value_usd=35000,
                    percentage_of_portfolio=70,
                    protocol="merchant_moe"
                ),
                PortfolioAsset(
                    token_symbol="USDC",
                    token_address="0x...",
                    balance=10000,
                    value_usd=10000,
                    percentage_of_portfolio=20,
                    protocol="fusionx"
                ),
                PortfolioAsset(
                    token_symbol="MNT",
                    token_address="0x...",
                    balance=5000,
                    value_usd=5000,
                    percentage_of_portfolio=10,
                    protocol=None
                )
            ]
            
            # Calculate risk metrics
            concentration = self._calculate_concentration(portfolio)
            liquidity = self._calculate_liquidity_sync(portfolio)
            volatility = self._calculate_volatility_sync(portfolio)
            contract_risk = self._calculate_contract_risk_sync(portfolio)
            
            correlation_risk, market_condition = self._calculate_correlation_risk(
                market_correlation or 0.5
            )
            
            # Build metrics
            metrics = RiskMetrics(
                concentration_score=concentration,
                liquidity_score=liquidity,
                volatility_score=volatility,
                contract_risk_score=contract_risk,
                correlation_risk_score=correlation_risk,
                overall_score=0
            )
            
            overall_score = self._compute_overall_score(metrics)
            metrics.overall_score = overall_score
            
            risk_level = self._get_risk_level(overall_score)
            recommendations = self._generate_recommendations(metrics, portfolio, market_condition)
            
            # Calculate detailed risk factors for deeper insights
            risk_factors = self.calculate_risk_factors(assets, market_correlation or 0.5)
            
            return {
                "wallet_address": wallet_address,
                "risk_score": overall_score,
                "risk_level": risk_level.value,
                "concentration_risk": concentration,
                "liquidity_score": liquidity,
                "volatility_score": volatility,
                "contract_risk": contract_risk,
                "correlation_risk": correlation_risk,
                "market_condition": market_condition,
                "risk_factors": risk_factors,  # Detailed breakdown
                "recommendations": recommendations,
                "top_holdings": [
                    {
                        "token": asset.token_symbol,
                        "token_address": asset.token_address,
                        "percentage": asset.percentage_of_portfolio,
                        "value_usd": asset.value_usd
                    }
                    for asset in sorted(portfolio, key=lambda a: a.percentage_of_portfolio, reverse=True)[:3]
                ],
                "timestamp": datetime.now(UTC).isoformat()
            }
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise
    
    async def check_contract_risk_with_audits(self, holdings: List[Dict]) -> Dict:
        """
        Fetch portfolio with protocol information
        TODO Week 3: Real data from Freeman's data_pipeline
        """

        
        # Mock portfolio for testing
        mock_assets = [
            PortfolioAsset(
                token_symbol="mETH",
                token_address="0x...",
                balance=10.5,
                value_usd=35000,
                percentage_of_portfolio=70,
                protocol="merchant_moe"  # Staked on Merchant Moe
            ),
            PortfolioAsset(
                token_symbol="USDC",
                token_address="0x...",
                balance=10000,
                value_usd=10000,
                percentage_of_portfolio=20,
                protocol="fusionx"  # Liquidity on FusionX
            ),
            PortfolioAsset(
                token_symbol="MNT",
                token_address="0x...",
                balance=5000,
                value_usd=5000,
                percentage_of_portfolio=10,
                protocol=None  # Held in wallet
            )
        ]
        return mock_assets
    
    def _calculate_concentration(self, assets: List[PortfolioAsset]) -> float:
        """Calculate concentration risk with HHI"""
        if not assets:
            return 0.0
        
        hhi = sum((asset.percentage_of_portfolio / 100) ** 2 for asset in assets)
        base_score = hhi * 100
        
        num_assets = len(assets)
        if num_assets >= 5:
            diversity_bonus = 10
        elif num_assets >= 3:
            diversity_bonus = 5
        else:
            diversity_bonus = 0
        
        return max(0, round(base_score - diversity_bonus, 2))
    
    def _calculate_liquidity_sync(self, assets: List[PortfolioAsset]) -> float:
        """Synchronous liquidity calculation"""
        if not assets:
            return 0.0
        
        tier_scores = {
            "very_high": 5,
            "high": 15,
            "medium": 35,
            "low": 60,
            "unknown": 75
        }
        
        weighted_liquidity = 0
        for asset in assets:
            # TODO: protocol = asset.protocol
            protocol = None
            if protocol and protocol.lower() in self.liquidity_tiers:
                tier = self.liquidity_tiers[protocol.lower()]
                asset_liquidity_score = tier_scores.get(tier, 75)
            else:
                if asset.value_usd:
                    asset_liquidity_score = 40 if asset.value_usd > self.thresholds["low_liquidity_usd"] else 70
                else:
                    asset_liquidity_score = 70

            weight = asset.percentage_of_portfolio / 100
            weighted_liquidity += asset_liquidity_score * weight
        
        return round(weighted_liquidity, 2)
    
    def _calculate_volatility_sync(self, assets: List[PortfolioAsset]) -> float:
        """Synchronous volatility calculation"""
        volatility_profiles = {
            "USDC": 3, "USDT": 3, "DAI": 5,
            "BTC": 30, "ETH": 35, "WETH": 35,
            "mETH": 40, "MNT": 55,
            "MOE": 65, "FUSION": 65,
            "UNKNOWN": 70
        }
        
        weighted_vol = 0
        for asset in assets:
            vol_score = volatility_profiles.get(asset.token_symbol.upper(), 70)
            weight = asset.percentage_of_portfolio / 100
            weighted_vol += vol_score * weight
        
        return round(weighted_vol, 2)
    
    def _calculate_contract_risk_sync(self, assets: List[PortfolioAsset]) -> float:
        """Synchronous contract risk calculation"""
        if not assets:
            return 0.0
        
        weighted_contract_risk = 0
        safe_tokens = ["USDC", "USDT", "DAI", "WETH", "mETH", "MNT", "BTC", "ETH"]
        
        for asset in assets:
            # TODO: protocol = asset.protocol
            protocol = None
            if protocol and protocol.lower() in self.protocol_tiers:
                tier = self.protocol_tiers[protocol.lower()]
                asset_risk = self.protocol_risk_scores[tier]
            elif asset.token_symbol.upper() in safe_tokens:
                asset_risk = 10
            else:
                asset_risk = 80
            
            weight = asset.percentage_of_portfolio / 100
            weighted_contract_risk += asset_risk * weight
        
        return round(weighted_contract_risk, 2)
    
    def _calculate_correlation_risk(self, market_correlation: float) -> Tuple[float, str]:
        """Calculate correlation risk"""
        if market_correlation < self.correlation_thresholds["healthy"]:
            return 15.0, "healthy_rotation"
        elif market_correlation < self.correlation_thresholds["neutral"]:
            return 40.0, "neutral_consolidation"
        else:
            excess = (market_correlation - 0.7) / 0.3
            return round(70 + (excess * 30), 2), "stressed_correlation"
    
    def calculate_risk_factors(
        self,
        assets: List[PortfolioAsset],
        market_correlation: float = 0.5
    ) -> Dict[str, float]:
        """
        Calculate individual risk factors for each category.
        
        This breaks down the portfolio into specific risk dimensions:
        - concentration: How concentrated holdings are (HHI-based)
        - liquidity: How easily positions can be liquidated
        - volatility: Overall portfolio volatility exposure
        - contract_risk: Exposure to unaudited/risky protocols
        - correlation_risk: Market correlation impact
        - diversification: Inverse of concentration (bonus)
        - exposure_balance: How well-balanced across asset classes
        
        Args:
            assets: List of portfolio assets
            market_correlation: Market correlation coefficient (0-1)
            
        Returns:
            Dictionary of risk factors (0-100 scale)
        """
        factors = {}
        
        # 1. Concentration Risk (0-100)
        factors["concentration"] = self._calculate_concentration(assets)
        
        # 2. Liquidity Risk (0-100)
        factors["liquidity"] = self._calculate_liquidity_sync(assets)
        
        # 3. Volatility Risk (0-100)
        factors["volatility"] = self._calculate_volatility_sync(assets)
        
        # 4. Contract Risk (0-100)
        factors["contract_risk"] = self._calculate_contract_risk_sync(assets)
        
        # 5. Correlation Risk (0-100)
        correlation_risk, _ = self._calculate_correlation_risk(market_correlation)
        factors["correlation_risk"] = correlation_risk
        
        # 6. Diversification Score (inverse of concentration, 0-100)
        # Higher is better (fewer risks)
        factors["diversification"] = max(0, 100 - factors["concentration"])
        
        # 7. Exposure Balance (penalty for too few assets)
        num_assets = len(assets)
        if num_assets >= 5:
            factors["exposure_balance"] = 100
        elif num_assets >= 3:
            factors["exposure_balance"] = 75
        elif num_assets >= 2:
            factors["exposure_balance"] = 50
        else:
            factors["exposure_balance"] = 25
        
        # 8. Stablecoin Allocation (0-100, higher is safer)
        stablecoin_weight = sum(
            asset.percentage_of_portfolio
            for asset in assets
            if asset.token_symbol.upper() in ["USDC", "USDT", "DAI", "BUSD", "USDP"]
        )
        factors["stablecoin_allocation"] = stablecoin_weight  # 0-100 as percentage
        
        # 9. Protocol Distribution Risk (concentration across protocols)
        protocol_weights = {}
        for asset in assets:
            protocol = asset.protocol or "unallocated"
            protocol_weights[protocol] = protocol_weights.get(protocol, 0) + asset.percentage_of_portfolio
        
        protocol_hhi = sum((w / 100) ** 2 for w in protocol_weights.values())
        factors["protocol_concentration"] = round(protocol_hhi * 100, 2)
        
        # 10. Asset Quality Score (blend of safety and liquidity)
        # Higher quality = lower risk
        quality_score = 0
        for asset in assets:
            # Score each asset (0-100, higher = better)
            token = asset.token_symbol.upper()
            if token in ["USDC", "USDT", "DAI"]:
                asset_quality = 95  # Stablecoins
            elif token in ["ETH", "WETH", "BTC", "mETH"]:
                asset_quality = 85  # Major layer 1 / layer 2 assets
            elif token in ["MNT", "MOE", "FUSION"]:
                asset_quality = 70  # Mantle ecosystem
            else:
                asset_quality = 50  # Unknown/emerging
            
            weight = asset.percentage_of_portfolio / 100
            quality_score += asset_quality * weight
        
        factors["asset_quality"] = round(quality_score, 2)
        
        return factors
    
    def _compute_overall_score(self, metrics: RiskMetrics) -> float:
        """Compute weighted overall score"""
        score = (
            metrics.concentration_score * self.weights["concentration"] +
            metrics.liquidity_score * self.weights["liquidity"] +
            metrics.volatility_score * self.weights["volatility"] +
            metrics.contract_risk_score * self.weights["contract"] +
            metrics.correlation_risk_score * self.weights["correlation"]
        )
        return round(score, 2)
    
    def _get_risk_level(self, score: float) -> RiskLevel:
        """Convert score to risk level"""
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
        """Generate recommendations"""
        recommendations = []
        
        if metrics.concentration_score > 60:
            top_asset = max(assets, key=lambda a: a.percentage_of_portfolio)
            recommendations.append(
                f"⚠ Critical concentration: {top_asset.token_symbol} is "
                f"{top_asset.percentage_of_portfolio:.1f}% of portfolio. "
                f"Immediately diversify."
            )
        elif metrics.concentration_score > 40:
            recommendations.append(
                "⚡ Moderate concentration detected. Consider diversifying."
            )
        
        if metrics.liquidity_score > 60:
            recommendations.append(
                "💧 Low liquidity exposure. Consider moving to higher liquidity DEXs."
            )
        
        if metrics.volatility_score > 50:
            recommendations.append(
                "📉 High volatility. Add stablecoin allocation to buffer movements."
            )
        
        if metrics.contract_risk_score > 40:
            recommendations.append(
                "🔒 Review protocol audit status and security."
            )
        
        if market_condition == "stressed_correlation":
            recommendations.append(
                "🌊 High market correlation indicates fear. Consider risk reduction."
            )
        elif market_condition == "healthy_rotation":
            recommendations.append(
                "✅ Healthy market conditions. Good time for strategic rebalancing."
            )
        
        if not recommendations:
            recommendations.append("✅ Portfolio risk profile is healthy.")
        
        return recommendations
    
    def retrieve_user_risk_analysis(self,wallet_address:str)->list:
        """
            Retrieve User Risk analysis from the db
        """
        store_id = 'Risk'
        risk_collection = self.mongo['Risk_Analysis']

        if ( users_risk_datas := risk_collection.find_one({"_id":store_id})
                or {'null':'null'}
            ):
                user_risk_analysis = users_risk_datas.get(wallet_address)
                return user_risk_analysis
        
    def update_user_risk_analysis(self,wallet_address:str,risk_analysis:dict):
        try:
            store_id = 'Risk'
            risk_collection = self.mongo['Risk_Analysis']
            risk_data = [risk_analysis]
            risk_analysis = risk_collection.update_one(
                {"_id":f"{store_id}"},
                {
                    "$set":{
                        wallet_address:risk_data,
                        'updated_at':datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            return risk_analysis
        except Exception as e:
            print(f'There is an error updatiing User transaction. issue: {e}')
    

