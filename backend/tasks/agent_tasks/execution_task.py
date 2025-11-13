"""
Execution Agent Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
# REMOVE THIS LINE: from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="execution_preview")
def execution_task(self, wallet_address: str, rebalance_plan: dict = None, alert_on_slippage: bool = True):
    """
    Generate execution preview with alert triggering
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Generating execution preview...', 'progress': 0}
        )
        
        print(f'Generating execution preview for: {wallet_address}')
        
        # Lazy import to avoid circular dependency
        from services.alert_manager import AlertManager
        
        alert_manager = AlertManager()
        
        # Run async execution preview
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Simulating trades on Mantle DEXs...', 'progress': 50}
        )
        
        # Generate execution preview (placeholder)
        # TODO: Implement actual execution preview
        execution_result = {
            'estimated_slippage': 0.5,
            'gas_cost_usd': 2.5,
            'liquidity_depth': 'high'
        }
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking execution alerts...', 'progress': 85}
        )
        
        # Trigger alerts for high slippage (placeholder)
        triggered_alerts = []
        
        loop.close()
        
        print(f'Execution preview completed')
        print(f'Triggered {len(triggered_alerts)} execution alerts')
        
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'execution_preview': execution_result,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'execution',
            'version': '2.0_with_alerts'
        }
        
    except Exception as e:
        print(f'Execution preview failed: {str(e)}')
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'execution'
        }
