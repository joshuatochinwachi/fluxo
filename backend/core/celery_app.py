from celery import Celery
from .config import Settings
from celery.schedules import crontab

# Celery Beat Periodic Task Schedule
celery_app.conf.beat_schedule = {
    # Monitor all tracked wallets every 15 minutes
    'periodic-portfolio-monitoring': {
        'task': 'periodic_portfolio_monitoring',
        'schedule': crontab(minute='*/15'),
        'args': ()
    },
    
    # Update market data every 5 minutes
    'update-market-data': {
        'task': 'periodic_market_update',
        'schedule': crontab(minute='*/5'),
        'args': ()
    },
    
    # Generate daily digest at 8 AM UTC
    'daily-digest-generation': {
        'task': 'generate_daily_digest',
        'schedule': crontab(hour=8, minute=0),
        'args': ()
    },
    
    # Check social sentiment every 30 minutes
    'sentiment-monitoring': {
        'task': 'periodic_sentiment_check',
        'schedule': crontab(minute='*/30'),
        'args': (['MNT', 'ETH', 'BTC'],)  # Top tokens to monitor
    },
}

# Task routing configuration
celery_app.conf.task_routes = {
    'tasks.risk_analysis': {'queue': 'risk_queue'},
    'tasks.social_analysis': {'queue': 'social_queue'},
    'tasks.macro_analysis': {'queue': 'macro_queue'},
    'tasks.*': {'queue': 'default'},
}

# ============= END OF ADDITIONS =============

settings = Settings()

# Create the Celery app using URLs defined in `core.config` so credentials
# and hosts can be managed through environment variables.
celery_app = Celery(
    "Backend-Worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_broker_url,
    include=[
        'tasks.agent_tasks.onchain_task',
        'tasks.agent_tasks.automation_task',
        'tasks.agent_tasks.execution_task',
        'tasks.agent_tasks.governance_task',
        'tasks.agent_tasks.macro_task',
        'tasks.agent_tasks.market_data_task',
        'tasks.agent_tasks.portfolio_task',
        'tasks.agent_tasks.research_task',
        'tasks.agent_tasks.risk_task',
        'tasks.agent_tasks.social_task',
        'tasks.agent_tasks.x402_task',
        'tasks.agent_tasks.yield_task'
    ],
)

# Also allow programmatic updates from CELERY_CONFIG if needed elsewhere.
celery_app.conf.update({
    'broker_url': settings.celery_broker_url,
    'result_backend': settings.celery_broker_url,
})
