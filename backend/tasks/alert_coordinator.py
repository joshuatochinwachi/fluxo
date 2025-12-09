"""
Alert Coordinator - Manages cross-agent alert triggering and batching
"""
import json
from core import celery_app
from celery import group, chain
import asyncio
from typing import List, Dict
from celery import chord


@celery_app.task(name="coordinate_alerts")
def coordinate_alerts(wallet_address: str, analysis_types: List[str] = None):
    """
    Coordinate multi-agent analysis with consolidated alerts
    
    Args:
        wallet_address: Wallet to analyze
        analysis_types: List of analyses to run ["risk", "social", "macro", "execution"]
    
    Returns:
        Consolidated alert report
    """
    if analysis_types is None:
        analysis_types = ["risk", "social", "macro"]
    
    print(f'Coordinating alerts for wallet: {wallet_address}')
    print(f'Analysis types: {analysis_types}')
    
    # Import tasks
    from tasks.agent_tasks.risk_task import risk_task
    from tasks.agent_tasks.social_task import social_task
    from tasks.agent_tasks.macro_task import macro_task
    
    # # Create parallel task group
    task_group = []
    
    if "risk" in analysis_types:
        task_group.append(risk_task.s(wallet_address))
    
    if "social" in analysis_types:
        # Analyze tokens in the portfolio
        task_group.append(social_task.s(wallet_address))  # TODO: Extract from portfolio
    
    if "macro" in analysis_types:
        task_group.append(macro_task.s(wallet_address))
    
    
    # Wait for all tasks to complete
    result = chord(task_group)(merge_alerts.s(wallet_address))
    return {
        'chord task_id':result.id
    }
    

@celery_app.task
def merge_alerts(results, wallet_address):
    """
    Merge all triggered alerts from multiple agents into a single consolidated alert.

    Args:
        results: List of task results from [risk_task, social_task, macro_task, ...]
        wallet_address: Wallet address being analyzed

    Returns:
        Consolidated alert structure stored in Redis
    """
    from api.models.alerts import ConsolidatedAlert, AgentSection, AlertSeverity
    import uuid
    
    print(f'Merging alerts for wallet: {wallet_address}')
    
    # Collect all alerts and metadata from each agent
    all_alerts = []
    agent_sections = []
    risk_factors_map = {}
    recommendations_set = set()
    risk_score = None
    risk_level = None
    market_condition = None
    analyses_completed = []
    max_severity = AlertSeverity.INFO
    
    for result in results:
        if not result:
            continue
        
        agent_name = result.get('agent', 'unknown')
        analyses_completed.append(agent_name)
        alerts = result.get('alerts', [])
        
        if alerts:
            all_alerts.extend(alerts)
            
            # Extract agent-specific info
            if agent_name == 'risk':
                risk_score = result.get('risk_analysis', {}).get('risk_score')
                risk_level = result.get('risk_analysis', {}).get('risk_level')
                market_condition = result.get('market_condition')
                risk_factors_map = result.get('risk_analysis', {}).get('risk_factors', {})
                
                # Extract recommendations
                recs = result.get('risk_analysis', {}).get('recommendations', [])
                recommendations_set.update(recs)
            
            # Determine highest severity from all alerts
            for alert in alerts:
                alert_severity = alert.get('severity', 'info')
                if alert_severity == 'critical':
                    max_severity = AlertSeverity.CRITICAL
                elif alert_severity == 'high' and max_severity != AlertSeverity.CRITICAL:
                    max_severity = AlertSeverity.HIGH
                elif alert_severity == 'warning' and max_severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                    max_severity = AlertSeverity.WARNING
            
            # Create a front-end friendly section for this agent and populate key metrics
            section_message = (alerts[0].get('title') + ': ' + alerts[0].get('message')) if alerts else f"No alerts from {agent_name}"

            key_metrics = {}
            

            # Agent-specific metrics
            if agent_name == 'risk':
                ra = result.get('risk_analysis', {})
                key_metrics = {
                    'risk_score': ra.get('risk_score'),
                    'risk_level': ra.get('risk_level'),
                    'top_holdings': ra.get('top_holdings', []),
                }
                # include recommendations
                recs = ra.get('recommendations', [])
                for r in recs:
                    recommendations_set.add(r)
            elif agent_name == 'macro':
                ma = result.get('macro_analysis', {})
                opportunities = ma.get('opportunities') if isinstance(ma, dict) else None
                key_metrics = {
                    'opportunities_count': len(opportunities) if opportunities else 0,
                    'top_opportunities': (opportunities or [])[:3]
                }
                # Add brief message when no alerts
                if not alerts and opportunities:
                    section_message = f"Found {len(opportunities)} opportunities; top {len((opportunities or [])[:3])} shown"
            elif agent_name == 'social':
                sa = result.get('sentiment_analysis', {})
                key_metrics = {
                    'overall_score': sa.get('overall_score'),
                    'trend': sa.get('trend') or sa.get('overall_sentiment'),
                    'volume_change': result.get('volume_change') or sa.get('volume_change'),
                    'message':sa.get('message')

                }

            section = AgentSection(
                agent_name=agent_name,
                section_title=f"{agent_name.capitalize()} Analysis",
                message=section_message,
                severity=max_severity,
                key_metrics=key_metrics,
                items=[]
            )
            agent_sections.append(section)
    
    # Build consolidated message
    message_lines = [
        f"Portfolio Analysis for {wallet_address}",
        f"Total Alerts Triggered: {len(all_alerts)} across {len(analyses_completed)} analyses",
        ""
    ]
    
    for section in agent_sections:
        message_lines.append(
            f"• {section.agent_name.upper()}: {len(section.items)} alert(s) - {section.severity.value.upper()}"
        )
    
    if recommendations_set:
        message_lines.append("\nTop Recommendations:")
        for idx, rec in enumerate(list(recommendations_set)[:5], 1):
            message_lines.append(f"  {idx}. {rec}")
    
    # Create consolidated alert
        consolidated_alert = ConsolidatedAlert(
        alert_id=str(uuid.uuid4()),
        wallet_address=wallet_address,
        title=f"Portfolio Analysis Report - {len(analyses_completed)} Analyses Completed",
        overall_severity=max_severity,
        agent_sections=agent_sections,
        total_alerts_triggered=len(all_alerts),
        risk_score=risk_score,
        risk_level=risk_level,
        market_condition=market_condition,
        message="\n".join(message_lines),
        risk_factors=risk_factors_map,
        recommendations=list(recommendations_set),
        timestamp=__import__('datetime').datetime.utcnow(),
        analyses_completed=analyses_completed,
        raw_alerts=[] # all_alerts
    )
    
    # Store the consolidated alert
    from services.alert_manager import AlertManager
    alert_manager = AlertManager()
    alert_manager.store_alert([consolidated_alert.to_dict()], wallet_address)
    
    print(f'Alert consolidation completed: {len(all_alerts)} alerts merged into 1 consolidated alert')
    
    return {
        'status': 'completed',
        'wallet_address': wallet_address,
        'total_alerts_triggered': len(all_alerts),
        'analyses_completed': analyses_completed,
        'consolidated_alert': consolidated_alert.to_dict(),
        'alert_id': consolidated_alert.alert_id
    }



@celery_app.task(name="batch_alert_processing")
def batch_alert_processing(wallet_addresses: List[str]):
    """
    Process alerts for multiple wallets in batch
    
    Args:
        wallet_addresses: List of wallets to monitor
    
    Returns:
        Batch processing summary
    """
    print(f'Batch processing alerts for {len(wallet_addresses)} wallets')
    
    
    results = []
    for wallet in wallet_addresses:
        task = coordinate_alerts.delay(wallet)
        results.append({
            'wallet': wallet,
            'task_id': task.id
        })


    print(f'Queued monitoring for {len(wallet_addresses)} wallets')
    
    return {
        'status': 'completed',
        'wallets_monitored': len(wallet_addresses),
        'tasks_queued': len(results),
        'task_ids': results
    }
    
