"""
Social Sentiment Analysis Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
# REMOVE THIS LINE: from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="social_analysis")
def social_task(self, token_symbol: str, platforms: list = None, alert_threshold: float = 0.7):
    """
    Social sentiment analysis with alert triggering
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching social sentiment...', 'progress': 0}
        )
        
        print(f'Running social sentiment analysis for: {token_symbol}')
        
        # Lazy import to avoid circular dependency
        from services.alert_manager import AlertManager
        from agents.social_agent import SocialAgent
        
        # Initialize agents
        social_agent = SocialAgent()
        alert_manager = AlertManager()
        
        # Default platforms
        if platforms is None:
            platforms = ["twitter", "farcaster", "reddit"]
        
        # Run async agent code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing sentiment across platforms...', 'progress': 30}
        )
        
        # Execute sentiment analysis (placeholder for now)
        # TODO: Implement actual sentiment analysis
        sentiment_result = {
            'overall_score': 0.7,
            'trend': 'positive',
            'volume_change': 1.2
        }
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking sentiment alerts...', 'progress': 70}
        )
        
        # Trigger alerts for extreme sentiment (placeholder)
        triggered_alerts = []
        
        loop.close()
        
        print(f'Social analysis completed: {sentiment_result["overall_score"]}')
        print(f'Triggered {len(triggered_alerts)} sentiment alerts')
        
        return {
            'status': 'completed',
            'token_symbol': token_symbol,
            'sentiment_analysis': sentiment_result,
            'platforms_analyzed': platforms,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'social',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Social analysis failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'social'
        }
