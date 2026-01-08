"""
Macro Market Analysis Celery Task - With Alert Triggering
"""
from multiprocessing import Value
from core import celery_app
import asyncio
# REMOVE THIS LINE: from services.alert_manager import AlertManager

@celery_app.task(
        bind=True,
        name="tasks.agent_tasks.macro_task.macro_task")
def macro_task(self, wallet_address: str = None):
    """
    Macro market analysis with Mantle protocol correlation
    """
    try:
   
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Fetching macro indicators...', 'progress': 0}
        )
        
        print(f'Running macro analysis On: {wallet_address or "all"}')
        
        # Lazy import to avoid circular dependency
        from agents.macro_agent import MacroAgent
        from agents.portfolio_agent import portfolio_agent
        from data_pipeline.pipeline import Pipeline
        
        # Initialize agents
        macro_agent = MacroAgent()
        portf = portfolio_agent()
        pipeline = Pipeline()

        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Analyzing market correlations...', 'progress': 40}
        # )
        
        # Execute macro analysis -> compute yield opportunities using MacroAgent
        from api.models.alerts import Alert, AlertType, AlertSeverity
        import uuid

        # Run the agent to fetch yield opportunities (pipeline preferred)
        # user_portfolio_data = loop.run_until_complete(
        #     pipeline.user_portfolio(wallet_address)
        # )
        user_portfolio_data = loop.run_until_complete( 
            portf.retrieve_portfolio_data(wallet_address)
        )
        macro_result = loop.run_until_complete(macro_agent.yield_opportunity(user_portfolio_data))

        # Create alerts for significant yield opportunities
        triggered_alerts = []
        try:
            opportunities = macro_result.get('opportunities') or []
            # threshold (percent) for triggering a yield opportunity alert
            threshold_percent = 4

            def normalize_apy_percent(v: float) -> float:
                try:
                    vv = float(v)
                except Exception:
                    return 0.0
                return vv * 100.0 if vv <= 1.0 else vv

            # Keep only the top-N opportunities by APY (highest first)
            TOP_N = 3

            def _apy_for_sort(o: dict) -> float:
                return normalize_apy_percent(o.get('apy', 0))

            # Sort descending and take top N
            top_opps = sorted(opportunities, key=_apy_for_sort, reverse=True)[:TOP_N]

            # Filter by threshold and aggregate into a single alert
            qualified_opps = [
                opp for opp in top_opps
                if normalize_apy_percent(opp.get('apy', 0)) >= threshold_percent
            ]

            if qualified_opps:
                # Build consolidated message with all top opportunities
                opp_details = []
                max_apy = 0.0
                for idx, opp in enumerate(qualified_opps, 1):
                    apy = normalize_apy_percent(opp.get('apy', 0))
                    max_apy = max(max_apy, apy)
                    opp_details.append(
                        f"{idx}. {opp.get('protocol_name') or opp.get('symbol')} - {apy:.2f}% APY"
                    )

                message = (
                    f"Top {len(qualified_opps)} yield opportunities found:\n" +
                    "\n".join(opp_details) +
                    f"\nConsider diversifying across these protocols for optimal returns."
                )

                # Create single consolidated alert
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    alert_type=AlertType.YIELD_OPPORTUNITY.value,
                    severity=AlertSeverity.INFO.value,
                    title=f"Top {len(qualified_opps)} Yield Opportunities ({max_apy:.2f}% max APY)",
                    message=message,
                    wallet_address=wallet_address,
                    current_value=max_apy,
                    threshold=threshold_percent,
                    details={"opportunities": qualified_opps, "count": len(qualified_opps)},
                    triggered_by="macro_agent"
                )
                try:
                    pass
                    # alert_manager._store_alert(alert)
                except Exception:
                    pass
                triggered_alerts.append(alert.to_dict())
        except Exception:
            # keep placeholder empty list if anything goes wrong
            triggered_alerts = []
        
        # self.update_state(
        #     state='PROCESSING',
        #     meta={'status': 'Checking correlation alerts...', 'progress': 80}
        # )
        
        loop.close()
        print(f"Macro Analysis Completed For Wallet {wallet_address}")
        print(f'Triggered {len(triggered_alerts)} macro alerts')
        
        return {
            'status': 'completed',
            'protocol': 'All Mantle Yield Protocol',
            'macro_analysis': macro_result,
            'alerts_triggered': len(triggered_alerts),
            'alerts': triggered_alerts,
            'agent': 'macro',
            'version': '2.0_with_alerts'
        }
    
    except Exception as e:
        print(f'Macro analysis failed: {str(e)}')
        
        # self.update_state(
        #     state='FAILURE',
        #     meta={'error': str(e)}
        # )
        
        return {
            'status': 'failed',
            'error': str(e),
            'agent': 'macro'
        }
