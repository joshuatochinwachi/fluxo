"""
Risk Analysis Celery Task - Enhanced with Alert Triggering
"""
from core import celery_app
import asyncio
from agents.risk_agent import RiskAgent
from services.alert_manager import AlertManager

@celery_app.task(bind=True, name="risk_analysis")
def risk_task(self, wallet_address: str, network: str = "mantle", market_correlation: float = None):
    """
    Enhanced background task with alert triggering
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing portfolio risk...', 'progress': 0}
        )
        
        print(f'Running risk analysis for wallet: {wallet_address}')
        
        # Initialize agents
        risk_agent = RiskAgent()
        alert_manager = AlertManager()
        
        # Run async agent code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Calculating risk factors...', 'progress': 40}
        )
        
        # Execute risk analysis
        risk_score = loop.run_until_complete(
            risk_agent.analyze_portfolio(wallet_address, market_correlation)
        )
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking alert triggers...', 'progress': 70}
        )
        
        # Check if any alerts should be triggered
        triggered_alerts = loop.run_until_complete(
            alert_manager.check_risk_alerts(
                wallet_address=wallet_address,
                risk_score=risk_score.score,
                risk_factors=risk_score.factors,
                market_condition=risk_score.market_condition
            )
        )
        
        loop.close()
        
        print(f'Risk analysis completed: Score {risk_score.score}')
        print(f'Triggered {len(triggered_alerts)} alerts')
        
        # Return result with alerts
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'network': network,
            'risk_analysis': risk_score.dict(),
            'market_condition': risk_score.market_condition,
            'alerts_triggered': len(triggered_alerts),
            'alerts': [alert.to_dict() for alert in triggered_alerts],
            'agent': 'risk',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Risk analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'risk'
        }
