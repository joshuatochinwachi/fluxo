"""
Macro Agent - Correlates macroeconomic indicators with DeFi market conditions
Implements Kelvin's correlation hypothesis for Risk Agent integration
Version: 2.0
"""

from core.config import REDIS_CONNECT, MONGO_CONNECT
from core.pubsub.channel_manager import ChannelNames
from data_pipeline.schemas.data_schemas import UserPortfolio
from typing import Dict, Any, List, Optional
from dataclasses import asdict
import json
import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class MacroAgent:
    """
    Analyzes macroeconomic conditions and correlates with DeFi markets.
    
    Key Responsibilities:
    1. Receive macro data via Redis pub/sub
    2. Analyze market conditions using Kelvin's correlation framework
    3. Provide correlation_risk_score to Risk Agent (10% weight)
    4. Store analysis in MongoDB for historical tracking
    """
    
    def __init__(self):
        self.redis_db = REDIS_CONNECT
        self.mongo_db = MONGO_CONNECT
        
        # Kelvin's correlation thresholds (from Risk Agent doc)
        self.correlation_thresholds = {
            "healthy": 0.4,    # <0.4 = Capital rotating (15 risk score)
            "neutral": 0.7,    # 0.4-0.7 = Consolidating (40 risk score)
            "stressed": 1.0    # >0.7 = Fear/herd behavior (70-100 risk score)
        }
        
        logger.info("✅ MacroAgent initialized")

    async def receive_macro_data(self):
        """
        Listen to macro data feed from data pipeline.
        
        Subscribes to: ChannelNames.MACRO
        Publishes to: macro_processed_channel
        """
        pubsub = self.redis_db.pubsub()
        await pubsub.subscribe(ChannelNames.MACRO.value)
        
        logger.info(f"📡 Subscribed to {ChannelNames.MACRO.value}")

        async for message in pubsub.listen():
            if message["type"] != "message":
                continue
                
            data = message["data"]
            logger.debug(f"📊 Received macro data: {data}")
            
            try:
                # Parse incoming data
                macro_data = json.loads(data) if isinstance(data, str) else data
                
                # Analyze market conditions
                analysis = await self.analyze_market_conditions(macro_data)
                
                # Store in MongoDB
                await self._store_analysis(analysis)
                
                # Publish to other agents
                await self.redis_db.publish(
                    "macro_processed_channel",
                    json.dumps(analysis)
                )
                
                logger.info(
                    f"✅ Market: {analysis['market_condition']} | "
                    f"Correlation Risk: {analysis['correlation_risk_score']}"
                )
                
            except Exception as e:
                logger.error(f"❌ Macro analysis failed: {str(e)}", exc_info=True)

    async def analyze_market_conditions(self, market_data: dict) -> dict:
        """
        Analyze market conditions using Kelvin's correlation hypothesis.
        
        Returns correlation_risk_score for Risk Agent (10% weight).
        """
        # Extract indicators
        btc_dom = market_data.get("btc_dominance", 50)
        dxy = market_data.get("dxy_index", 100)
        eth_btc_ratio = market_data.get("eth_btc_ratio", 0.05)
        
        # Calculate correlation
        correlation = min(btc_dom / 60, 1.0)
        
        # Determine market condition and risk score
        if correlation < self.correlation_thresholds["healthy"]:
            condition = "healthy_rotation"
            risk_level = "low"
            correlation_risk_score = 15
            
        elif correlation < self.correlation_thresholds["neutral"]:
            condition = "neutral_consolidation"
            risk_level = "medium"
            correlation_risk_score = 40
            
        else:
            condition = "stressed_correlation"
            risk_level = "high"
            correlation_risk_score = min(70 + ((correlation - 0.7) * 100), 100)
        
        analysis = {
            "market_condition": condition,
            "risk_level": risk_level,
            "correlation_risk_score": correlation_risk_score,
            "btc_correlation": round(correlation, 3),
            "indicators": {
                "btc_dominance": round(btc_dom, 2),
                "dxy_index": round(dxy, 2),
                "eth_btc_ratio": round(eth_btc_ratio, 4)
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "agent": "macro_agent"
        }
        
        return analysis

    async def yield_opportunity(
        self, 
        portfolio_data: Optional[List[UserPortfolio]] = None
    ) -> Dict[str, Any]:
        """
        Find Mantle yield opportunities based on pipeline data.
        
        Called by: Risk Agent after portfolio analysis
        """
        try:
            yield_collection = self.mongo_db["Yield_Protocol"]
        except Exception:
            return {"opportunities": [], "summary": "mongo_unavailable"}

        store_id = "Mantle_yield_protocol"
        yield_protocol_data = yield_collection.find_one({"_id": store_id})

        if not yield_protocol_data:
            return {"opportunities": [], "summary": "no_pipeline_data"}

        protocols = (
            yield_protocol_data.get("protocol") or
            yield_protocol_data.get("yield_protocols") or
            []
        )

        # Normalize portfolio tokens
        portfolio_tokens = set()
        if portfolio_data:
            for asset in [asdict(data) for data in portfolio_data]:
                symbol = (asset.get("symbol") or "").lower()
                if symbol:
                    portfolio_tokens.add(symbol)

        def apy_of(p: Dict[str, Any]) -> float:
            try:
                return float(p.get("apy", 0) or p.get("estimated_apy", 0) or 0)
            except:
                return 0.0

        top_by_apy = sorted(protocols, key=apy_of, reverse=True)[:20]

        opportunities = []
        for proto in top_by_apy:
            symbol = (proto.get("symbol") or "").lower()
            apy = apy_of(proto)
            matched = symbol in portfolio_tokens
            
            existing_allocation = 0.0
            if matched and portfolio_data:
                for asset in [asdict(data) for data in portfolio_data]:
                    if (asset.get("symbol") or "").lower() == symbol:
                        existing_allocation = float(asset.get("percentage_of_portfolio") or 0)
                        break

            action = "consider_rebalancing" if matched else "consider_entering"

            opportunities.append({
                "protocol_name": proto.get("project") or proto.get("protocol"),
                "symbol": proto.get("symbol"),
                "apy": round(apy, 2),
                "tvl_usd": proto.get("tvl_usd", 0),
                "existing_allocation": existing_allocation,
                "matched_with_portfolio": matched,
                "recommended_action": action,
                "source": "DeFiLlama"
            })

        summary = {
            "num_protocols": len(protocols),
            "num_opportunities": len(opportunities),
            "top_apy": opportunities[0]["apy"] if opportunities else 0
        }

        return {"opportunities": opportunities, "summary": summary}

    async def _store_analysis(self, analysis: dict):
        """Store macro analysis in MongoDB"""
        try:
            macro_collection = self.mongo_db["Macro_Analysis"]
            macro_collection.insert_one(analysis.copy())
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")

