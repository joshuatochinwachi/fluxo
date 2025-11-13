"""
Execution Agent Celery Task - With Alert Triggering
"""
from core import celery_app
import asyncio
from agents.execution_agent import ExecutionAgent
from services.alert_manager import AlertManager


@celery_app.task(bind=True, name="execution_preview")
def execution_task(self, wallet_address: str, rebalance_plan: dict, alert_on_slippage: bool = True):
    """
    Generate execution preview with alert triggering
    
    Args:
        wallet_address: Wallet to rebalance
        rebalance_plan: Proposed rebalancing actions
        alert_on_slippage: Alert if slippage exceeds threshold
    """
    try:
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Generating execution preview...', 'progress': 0}
        )
        
        print(f'Generating execution preview for: {wallet_address}')
        
        # Lazy import
        from services.alert_manager import AlertManager
        
        # Initialize agents
        execution_agent = ExecutionAgent()
        alert_manager = AlertManager()
        
        # Run async execution preview
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Simulating trades on Mantle DEXs...', 'progress': 50}
        )
        
        # Generate execution preview
        execution_result = loop.run_until_complete(
            execution_agent.generate_preview(
                wallet_address=wallet_address,
                rebalance_plan=rebalance_plan
            )
        )
        
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Checking execution alerts...', 'progress': 85}
        )
        
        # Trigger alerts for high slippage or poor execution
        triggered_alerts = []
        if alert_on_slippage:
            triggered_alerts = loop.run_until_complete(
                alert_manager.check_execution_alerts(
                    wallet_address=wallet_address,
                    expected_slippage=execution_result.estimated_slippage,
                    gas_cost=execution_result.gas_cost_usd,
                    liquidity_depth=execution_result.liquidity_depth
                )
            )
        
        loop.close()
        
        print(f'Execution preview completed')
        print(f'Triggered {len(triggered_alerts)} execution alerts')
        
        return {
            'status': 'completed',
            'wallet_address': wallet_address,
            'execution_preview': execution_result.dict(),
            'alerts_triggered': len(triggered_alerts),
            'alerts': [alert.to_dict() for alert in triggered_alerts],
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
