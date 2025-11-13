"""
Macro Market Analysis Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
from agents.macro_agent import MacroAgent
from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="macro_analysis")
def macro_task(self, protocol: str = None, alert_on_correlation: bool = True):
    """
    Macro market analysis with Mantle protocol correlation
    
    Args:
        protocol: Specific Mantle protocol to analyze (optional)
        alert_on_correlation: Trigger alerts on high correlation events
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching macro indicators...', 'progress': 0}
        )
        
        print(f'Running macro analysis for protocol: {protocol or "all"}')
        
        # Lazy import
        from services.alert_manager import AlertManager
        
        # Initialize agents
        macro_agent = MacroAgent()
        alert_manager = AlertManager()
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing market correlations...', 'progress': 40}
        )
        
        # Execute macro analysis
        macro_result = loop.run_until_complete(
            macro_agent.analyze_market_conditions(protocol=protocol)
        )
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking correlation alerts...', 'progress': 80}
        )
        
        # Trigger alerts for significant market shifts
        triggered_alerts = []
        if alert_on_correlation:
            triggered_alerts = loop.run_until_complete(
                alert_manager.check_macro_alerts(
                    market_condition=macro_result.market_condition,
                    correlation_score=macro_result.correlation_score,
                    mantle_yield_impact=macro_result.yield_impact,
                    protocol=protocol
                )
            )
        
        loop.close()
        
        print(f'Macro analysis completed: {macro_result.market_condition}')
        print(f'Triggered {len(triggered_alerts)} macro alerts')
        
        return {
            'status': 'completed',
            'protocol': protocol or 'all_mantle_protocols',
            'macro_analysis': macro_result.dict(),
            'alerts_triggered': len(triggered_alerts),
            'alerts': [alert.to_dict() for alert in triggered_alerts],
            'agent': 'macro',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Macro analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'macro'
        }
