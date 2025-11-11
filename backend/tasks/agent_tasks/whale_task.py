"""
Whale Tracking Celery Task
Monitors whale movements and triggers alerts
"""
from core import celery_app
import asyncio
from services.whale_tracker import WhaleTracker, DataSource

@celery_app.task(bind=True, name="whale_tracking")
def whale_task(self, timeframe: str = "24h", min_value_usd: float = 100_000):
    """
    Background task for whale movement detection and alerts
    
    Args:
        timeframe: Time period to analyze ("1h", "24h", "7d")
        min_value_usd: Minimum transaction value to track
    
    Returns:
        dict: Whale movements and triggered alerts
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching whale movements...', 'progress': 0}
        )
        
        print(f'Running whale tracking (timeframe: {timeframe})')
        
        # Lazy import
        from services.alert_manager import AlertManager
        
        # Initialize tracker
        tracker = WhaleTracker(primary_source=DataSource.MOCK)
        alert_manager = AlertManager()
        
        # Run async code
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Analyzing whale movements...', 'progress': 50}
        )
        
        # Get whale movements
        movements = loop.run_until_complete(
            tracker.get_recent_movements(timeframe, min_value_usd)
        )
        
        # Check for alerts
        whale_alerts = loop.run_until_complete(
            tracker.check_whale_alerts(movements)
        )
        
        # Store alerts
        for alert in whale_alerts:
            alert_manager._store_alert(alert)
        
        loop.close()
        
        print(f'Whale tracking completed: {len(movements)} movements, {len(whale_alerts)} alerts')
        
        # Get summary
        summary = tracker.get_summary(movements)
        
        return {
            'status': 'completed',
            'timeframe': timeframe,
            'movements_detected': len(movements),
            'alerts_triggered': len(whale_alerts),
            'total_volume_usd': summary['total_volume_usd'],
            'movements': [m.to_dict() for m in movements],
            'alerts': [alert.to_dict() for alert in whale_alerts],
            'summary': summary,
            'agent': 'whale_tracker'
        }
        
    except Exception as e:
        print(f'Whale tracking failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'whale_tracker'
        }
