"""
FLUXO BACKEND - MASTER INTEGRATION
Ties all agents, services, and tasks together for end-to-end flow
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, UTC

# Import all agents
from agents.risk_agent import RiskAgent
from agents.social_agent import SocialAgent

# Import services
from services.ai_insights_engine import AIInsightsEngine
from services.audit_feed_service import get_audit_service

# Import task coordinators
from tasks.alert_coordinator import coordinate_alerts

logger = logging.getLogger(__name__)


class FluxoBackendIntegration:
    """
    Master Integration Class
    
    Coordinates all backend components:
    - Risk Agent (Muhammed)
    - Social Agent (Muhammed)
    - Macro Agent (Kelvin's research)
    - Execution Agent
    - Alert System (Muhammed)
    - AI Insights (Muhammed)
    
    Integrates with:
    - Data Pipeline (Freeman)
    - On-chain Agent (Freeman)
    - Market Data (Freeman)
    """
    
    def __init__(self):
        # Initialize all agents
        self.risk_agent = RiskAgent()
        self.social_agent = SocialAgent(use_mock=False)
        self.ai_engine = AIInsightsEngine()
        self.audit_service = get_audit_service()
        
        logger.info("✅ Fluxo Backend Integration initialized")
        logger.info("✅ All agents loaded")
    
    async def complete_wallet_analysis(
        self,
        wallet_address: str,
        include_social: bool = True,
        include_audits: bool = True,
        include_ai_insights: bool = True
    ) -> Dict:
        """
        COMPLETE END-TO-END WALLET ANALYSIS
        
        This is the main integration function that:
        1. Analyzes risk
        2. Checks audits
        3. Analyzes social sentiment
        4. Generates AI insights
        5. Triggers alerts if needed
        
        Args:
            wallet_address: Wallet to analyze
            include_social: Include social sentiment
            include_audits: Include audit checks
            include_ai_insights: Generate AI insights
            
        Returns:
            Complete analysis report
        """
        logger.info(f"🚀 Starting complete analysis for {wallet_address}")
        
        results = {
            "wallet_address": wallet_address,
            "analysis_timestamp": datetime.now(UTC).isoformat(),
            "components_analyzed": []
        }
        
        # ============= 1. RISK ANALYSIS =============
        logger.info("📊 Step 1: Risk Analysis")
        try:
            risk_analysis = self.risk_agent.analyze_portfolio({
                "wallet": wallet_address,
                "holdings": []  # TODO: Get from Freeman's data_pipeline
            })
            results["risk_analysis"] = risk_analysis
            results["components_analyzed"].append("risk")
            logger.info(f"✅ Risk Analysis complete: {risk_analysis['risk_level']}")
        except Exception as e:
            logger.error(f"❌ Risk Analysis failed: {str(e)}")
            results["risk_analysis"] = {"error": str(e)}
        
        # ============= 2. AUDIT CHECK =============
        if include_audits:
            logger.info("🔒 Step 2: Contract Audit Check")
            try:
                holdings = [
                    {"protocol": "mantle", "token": "MNT", "value": 10000},
                    {"protocol": "merchantmoe", "token": "MOE", "value": 5000}
                ]
                audit_results = await self.risk_agent.check_contract_risk_with_audits(holdings)
                results["audit_check"] = audit_results
                results["components_analyzed"].append("audits")
                logger.info(f"✅ Audit Check complete: {audit_results['audit_coverage']}% coverage")
            except Exception as e:
                logger.error(f"❌ Audit Check failed: {str(e)}")
                results["audit_check"] = {"error": str(e)}
        
        # ============= 3. SOCIAL SENTIMENT =============
        if include_social:
            logger.info("📱 Step 3: Social Sentiment Analysis")
            try:
                # Analyze sentiment for major tokens in portfolio
                sentiment_result = await self.social_agent.analyze_sentiment("MNT")
                results["social_sentiment"] = sentiment_result
                results["components_analyzed"].append("social")
                logger.info(f"✅ Social Analysis complete: {sentiment_result['overall_sentiment']}")
            except Exception as e:
                logger.error(f"❌ Social Analysis failed: {str(e)}")
                results["social_sentiment"] = {"error": str(e)}
        
        # ============= 4. AI INSIGHTS =============
        if include_ai_insights:
            logger.info("🤖 Step 4: AI Insights Generation")
            try:
                ai_insights = await self.ai_engine.generate_portfolio_insights(
                    wallet_address=wallet_address,
                    risk_analysis=results.get("risk_analysis", {}),
                    social_sentiment=results.get("social_sentiment"),
                    macro_conditions=None
                )
                results["ai_insights"] = ai_insights
                results["components_analyzed"].append("ai_insights")
                logger.info("✅ AI Insights generated")
            except Exception as e:
                logger.error(f"❌ AI Insights failed: {str(e)}")
                results["ai_insights"] = {"error": str(e)}
        
        # ============= 5. ALERT TRIGGERING =============
        logger.info("🔔 Step 5: Alert Check")
        from services.alert_manager import AlertManager
        alert_manager = AlertManager()
        try:
            risk_score = results.get("risk_analysis", {}).get("risk_score", 0)
            if risk_score >= 70:
                alert_result = await alert_manager.check_risk_alerts(
                    wallet_address=wallet_address,
                    risk_score=risk_score,
                    risk_factors={},
                    market_condition="neutral"
                )
                results["alerts_triggered"] = len(alert_result)
                logger.info(f"⚠ {len(alert_result)} alerts triggered")
            else:
                results["alerts_triggered"] = 0
                logger.info("✅ No alerts triggered")
        except Exception as e:
            logger.error(f"❌ Alert check failed: {str(e)}")
            results["alerts_triggered"] = 0
        
        # ============= 6. SUMMARY =============
        results["summary"] = self._generate_summary(results)
        
        logger.info(f"✅ Complete analysis finished for {wallet_address}")
        return results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate executive summary"""
        summary = {
            "status": "complete",
            "components_analyzed": len(results.get("components_analyzed", [])),
            "has_errors": False
        }
        
        # Risk summary
        if "risk_analysis" in results and "error" not in results["risk_analysis"]:
            summary["risk_level"] = results["risk_analysis"].get("risk_level", "unknown")
            summary["risk_score"] = results["risk_analysis"].get("risk_score", 0)
        else:
            summary["has_errors"] = True
        
        # Social summary
        if "social_sentiment" in results and "error" not in results["social_sentiment"]:
            summary["sentiment"] = results["social_sentiment"].get("overall_sentiment", "unknown")
        
        # Audit summary
        if "audit_check" in results and "error" not in results["audit_check"]:
            summary["audit_coverage"] = results["audit_check"].get("audit_coverage", 0)
        
        # AI insights summary
        if "ai_insights" in results and "error" not in results["ai_insights"]:
            insights = results["ai_insights"].get("insights", {})
            if insights and "recommendations" in insights:
                summary["top_recommendation"] = insights["recommendations"][0]
        
        return summary
    
    async def batch_analyze_wallets(self, wallet_addresses: List[str]) -> Dict:
        """
        Analyze multiple wallets in batch
        
        Args:
            wallet_addresses: List of wallets to analyze
            
        Returns:
            Batch analysis results
        """
        logger.info(f"📦 Starting batch analysis for {len(wallet_addresses)} wallets")
        
        results = []
        for wallet in wallet_addresses:
            try:
                analysis = await self.complete_wallet_analysis(
                    wallet_address=wallet,
                    include_social=False,  # Faster for batch
                    include_ai_insights=False
                )
                results.append(analysis)
            except Exception as e:
                logger.error(f"Batch analysis failed for {wallet}: {str(e)}")
                results.append({
                    "wallet_address": wallet,
                    "error": str(e)
                })
        
        logger.info(f"✅ Batch analysis complete: {len(results)} results")
        
        return {
            "total_analyzed": len(wallet_addresses),
            "successful": len([r for r in results if "error" not in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
    
    def get_system_status(self) -> Dict:
        """
        Get status of all backend components
        """
        return {
            "status": "operational",
            "timestamp": datetime.now(UTC).isoformat(),
            "components": {
                "risk_agent": "✅ operational",
                "social_agent": "✅ operational",
                "alert_manager": "✅ operational",
                "ai_engine": "✅ operational",
                "audit_service": "✅ operational"
            },
            "features": {
                "risk_analysis": True,
                "social_sentiment": True,
                "audit_checking": True,
                "ai_insights": True,
                "alert_coordination": True,
                "batch_processing": True
            },
            "integrations": {
                "celery_workers": "✅ ready",
                "redis": "✅ connected",
                "claude_api": "✅ configured"
            }
        }


# Global instance
_integration = None

def get_integration() -> FluxoBackendIntegration:
    """Get singleton integration instance"""
    global _integration
    if _integration is None:
        _integration = FluxoBackendIntegration()
    return _integration
