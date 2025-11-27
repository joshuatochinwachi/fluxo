"""
Periodic Tasks for Continuous Monitoring
"""
from core import celery_app
import asyncio
import json


@celery_app.task(name="periodic_portfolio_monitoring")
def periodic_portfolio_monitoring():
    """
    Periodic task to monitor all tracked portfolios
    Runs every 15 minutes via Celery Beat
    """
    try:
        print('Starting periodic portfolio monitoring...')
        
        # Get tracked wallets from Redis
       
        from core.config import get_redis_connection
        redis_conn = get_redis_connection()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get all tracked wallets
        tracked_wallets = loop.run_until_complete(
            redis_conn.smembers("tracked_wallets")
        )
        
        loop.close()
        
        if not tracked_wallets:
            print('No wallets being tracked')
            return {
                'status': 'no_wallets',
                'message': 'No wallets in tracking list'
            }
        
        # Queue alert coordination for each wallet
        from tasks.alert_coordinator import coordinate_alerts
        
        results = []
        for wallet in tracked_wallets:
            task = coordinate_alerts.delay(wallet.decode())
            results.append({
                'wallet': wallet,
                'task_id': task.id
            })

        print(f'Queued monitoring for {len(tracked_wallets)} wallets')
        
        return {
            'status': 'completed',
            'wallets_monitored': len(tracked_wallets),
            'tasks_queued': len(results),
            'task_ids': results
        }
        
    except Exception as e:
        print(f'Periodic monitoring failed: {str(e)}')
        return {
            'status': 'failed',
            'error': str(e)
        }


@celery_app.task(name="periodic_market_update")
def periodic_market_update():
    """
    Update market data every 5 minutes
    """
    try:
        print('Updating market data...')
        
        from tasks.agent_tasks.macro_task import macro_task
        
        # Run macro analysis
        task = macro_task.delay()
        
        return {
            'status': 'completed',
            'task_id': task.id,
            'message': 'Market data update queued'
        }
        
    except Exception as e:
        print(f'Market update failed: {str(e)}')
        return {
            'status': 'failed',
            'error': str(e)
        }


@celery_app.task(name="periodic_sentiment_check")
def periodic_sentiment_check(tokens: list):
    """
    Check sentiment for major tokens every 30 minutes
    """
    try:
        print(f'Checking sentiment for tokens: {tokens}')
        
        from tasks.agent_tasks.social_task import social_task
        
        results = []
        for token in tokens:
            task = social_task.delay(token)
            results.append({
                'token': token,
                'task_id': task.id
            })
        
        return {
            'status': 'completed',
            'tokens_analyzed': len(tokens),
            'tasks': results
        }
        
    except Exception as e:
        print(f'Sentiment check failed: {str(e)}')
        return {
            'status': 'failed',
            'error': str(e)
        }


@celery_app.task(name="generate_daily_digest")
def generate_daily_digest():
    """
    Generate daily digest at 8 AM UTC
    """
    try:
        print('Generating daily digest...')
        
        # Get all tracked wallets
        
        from core.config import get_redis_connection
        redis_conn = get_redis_connection()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        
        tracked_wallets = loop.run_until_complete(
            redis_conn.smembers("tracked_wallets")
        )
        
        # Generate digest for each wallet
        # TODO: Integrate with x402 for encrypted delivery
        digests_generated = []
        
        for wallet in tracked_wallets:
            # Get latest analysis results
            risk_key = f"risk_analysis:{wallet}"
            risk_data = loop.run_until_complete(
                redis_conn.get(risk_key)
            )
            
            if risk_data:
                digest = {
                    'wallet': wallet,
                    'date': '2025-11-13',
                    'risk_summary': json.loads(risk_data),
                    'type': 'daily_digest'
                }
                digests_generated.append(digest)
        
        loop.close()
        
        print(f'Generated {len(digests_generated)} digests')
        
        return {
            'status': 'completed',
            'digests_generated': len(digests_generated),
            'wallets': list(tracked_wallets)
        }
        
    except Exception as e:
        print(f'Digest generation failed: {str(e)}')
        return {
            'status': 'failed',
            'error': str(e)
        }
