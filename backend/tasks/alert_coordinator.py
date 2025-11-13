"""
Alert Coordinator - Manages cross-agent alert triggering and batching
"""
from core import celery_app
from celery import group, chain
import asyncio
from typing import List, Dict
from services.alert_manager import AlertManager


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
    
    # Create parallel task group
    task_group = []
    
    if "risk" in analysis_types:
        task_group.append(risk_task.s(wallet_address))
    
    if "social" in analysis_types:
        # Analyze tokens in the portfolio
        task_group.append(social_task.s("MNT"))  # TODO: Extract from portfolio
    
    if "macro" in analysis_types:
        task_group.append(macro_task.s())
    
    # Execute all tasks in parallel
    job = group(task_group)
    result = job.apply_async()
    
    # Wait for all tasks to complete
    results = result.get(timeout=300)  # 5 minute timeout
    
    # Consolidate alerts
    all_alerts = []
    for task_result in results:
        if task_result.get('alerts'):
            all_alerts.extend(task_result['alerts'])
    
    print(f'Alert coordination completed: {len(all_alerts)} total alerts')
    
    return {
        'status': 'completed',
        'wallet_address': wallet_address,
        'total_alerts': len(all_alerts),
        'alerts_by_type': {
            'risk': len([a for a in all_alerts if a.get('type') == 'risk']),
            'sentiment': len([a for a in all_alerts if a.get('type') == 'sentiment']),
            'macro': len([a for a in all_alerts if a.get('type') == 'macro']),
        },
        'all_alerts': all_alerts,
        'analyses_completed': len(results)
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
    
    # Queue individual alert coordination for each wallet
    tasks = [coordinate_alerts.s(wallet) for wallet in wallet_addresses]
    
    # Execute batch
    job = group(tasks)
    result = job.apply_async()
    
    # Collect results
    results = result.get(timeout=600)  # 10 minute timeout for batch
    
    # Summarize
    total_alerts = sum(r.get('total_alerts', 0) for r in results)
    
    return {
        'status': 'completed',
        'wallets_processed': len(wallet_addresses),
        'total_alerts_triggered': total_alerts,
        'summary': results
    }
