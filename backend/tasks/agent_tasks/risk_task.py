"""
Risk Analysis Celery Task - Enhanced with Alert Triggering
"""

from core import celery_app
import asyncio
@celery_app.task(bind=True, name="risk_analysis")
def risk_task(self, wallet_address: str, network: str = "mantle", market_correlation: float = None):
    """
    Enhanced background task with alert triggering
    """
    # try:
    self.update_state(
        state='PROCESSING',
        meta={'status': 'Analyzing portfolio risk...', 'progress': 0}
    )
    
    print(f'Running risk analysis for wallet: {wallet_address}')

    # lazy import to avoidd circular dependency
    from agents.portfolio_agent import portfolio_agent
    from agents.risk_agent import RiskAgent
    from services.alert_manager import AlertManager
    
    # Initialize agents
    portf_agent = portfolio_agent()
    risk_agent = RiskAgent()
    alert_manager = AlertManager()
    
    # Run async agent code
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    self.update_state(
        state='PROCESSING',
        meta={'status': 'Calculating risk factors...', 'progress': 40}
    )
    
    # Fetch user portolio
    portfolio =  loop.run_until_complete(
        portf_agent.analyze_portfolio(wallet_address)
    )

    # Execute risk analysis
    risk_score = risk_agent.analyze_portfolio(portfolio, market_correlation)
    
    self.update_state(
        state='PROCESSING',
        meta={'status': 'Checking alert triggers...', 'progress': 70}
    )
    
    # Check if any alerts should be triggered
    triggered_alerts_list = loop.run_until_complete(
        alert_manager.check_risk_alerts(
            wallet_address=wallet_address,
            risk_score=risk_score.get('risk_score', 0),
            risk_factors=risk_score.get('risk_factors', {}),
            market_condition=risk_score.get('market_condition', 'Neutral')
        )
    )
    
    # Consolidate multiple alerts into a single aggregated alert
    from api.models.alerts import Alert, AlertType, AlertSeverity
    import uuid
    
    consolidated_alert = None
    if triggered_alerts_list:
        # Build consolidated message from all triggered alerts
        alert_summaries = []
        max_severity = AlertSeverity.INFO
        risk_factors_details = {}
        
        for alert in triggered_alerts_list:
            alert_summaries.append(f"• {alert.title}: {alert.message}")
            
            # Track highest severity
            if alert.severity == AlertSeverity.CRITICAL:
                max_severity = AlertSeverity.CRITICAL
            elif alert.severity == AlertSeverity.HIGH and max_severity != AlertSeverity.CRITICAL:
                max_severity = AlertSeverity.HIGH
            elif alert.severity == AlertSeverity.WARNING and max_severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                max_severity = AlertSeverity.WARNING
            
            # Collect risk factor details
            if alert.details:
                risk_factors_details.update(alert.details)
        
        # Create single consolidated alert
        consolidated_alert = Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=AlertType.HIGH_RISK_SCORE,
            severity=max_severity,
            title=f"Portfolio Risk Assessment - {len(triggered_alerts_list)} Risk Factor(s) Detected",
            message=(
                f"Your portfolio has triggered {len(triggered_alerts_list)} risk alert(s):\n\n" +
                "\n".join(alert_summaries) +
                "\n\nRecommended Actions:\n" +
                "\n".join([f"✓ {rec}" for rec in risk_score.get('recommendations', [])])
            ),
            wallet_address=wallet_address,
            current_value=risk_score.get('risk_score', 0),
            threshold=70.0,
            details={
                "alerts_count": len(triggered_alerts_list),
                "risk_score": risk_score.get('risk_score', 0),
                "risk_level": risk_score.get('risk_level', 'unknown'),
                "risk_factors": risk_score.get('risk_factors', {}),
                "market_condition": risk_score.get('market_condition', 'Neutral'),
                "consolidated_from": len(triggered_alerts_list)
            },
            triggered_by="risk_agent"
        )
    
    loop.close()
    
    print(f'Risk analysis completed: Score {risk_score.get("risk_score", 0)}')
    print(f'Triggered {len(triggered_alerts_list)} risk factors, consolidated into 1 alert')
    
    # Return result with consolidated alert
    consolidated_alerts = [consolidated_alert.to_dict()] if consolidated_alert else []
    
    return {
        'status': 'completed',
        'wallet_address': wallet_address,
        'network': network,
        'risk_analysis': risk_score,
        'market_condition': risk_score.get('market_condition', 'Neutral'),
        'alerts_triggered': len(triggered_alerts_list),
        'alerts_consolidated': 1 if consolidated_alert else 0,
        'alerts': consolidated_alerts,
        'agent': 'risk',
        'version': '2.0_with_consolidated_alerts'
    }
            
    # except Exception as e:
    #     print(f'Risk analysis failed: {str(e)}')
        
    #     # self.update_state(
    #     #     state='FAILURE',
    #     #     meta={'error': str(e)}
    #     # )
        
    #     return {
    #         'status': 'failed',
    #         'error': str(e),
    #         'agent': 'risk'
    #     }
