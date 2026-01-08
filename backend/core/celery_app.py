from celery import Celery
from .config import Settings
import sys,os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

settings = Settings()


# Create the Celery app using URLs defined in core.config so credentials
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
        'tasks.agent_tasks.yield_task',
        # 'tasks.alert_coordinator',
        'tasks.periodic_tasks',
        'tasks.agent_tasks.pipeline_task',
        'tasks.alert_coordinator',
        'tasks.digest_tasks'
    ],
)


# Also allow programmatic updates from CELERY_CONFIG if needed elsewhere.
celery_app.conf.update({
    'broker_url': settings.celery_broker_url,
    'result_backend': settings.celery_broker_url,
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    # 'enable_utc': True,
    # 'task_track_started': True,
    # 'task_time_limit': 300,
    # 'task_soft_time_limit': 240,
    # 'worker_prefetch_multiplier': 4,
    # 'worker_max_tasks_per_child': 1000,
})



celery_app.conf.beat_schedule = {
    
    'Mantle_Yield':{
        'task':'tasks.agent_tasks.pipeline_task.mantle_yield',
        'schedule':100,
        'args':()
    },

    'user_portfolio':{
        'task':'tasks.agent_tasks.portfolio_task.portfolio_task',
        'schedule':186,
        'args':()
    },

    'Risk_Analysis':{
        'task':'tasks.agent_tasks.risk_task.risk_task',
        'schedule':20,
        'args':()
    },

    'digest_task':{
        'task':'tasks.digest_tasks.daily_news_digest',
        'schedule':180,
        'args':()
    },

    'periodic_Alert_task':{
        'task':'tasks.periodic_tasks.periodic_portfolio_monitoring',
        'schedule':60,
        'args':()
    },
    
    # 'test macro':{
    #     'task':'tasks.agent_tasks.macro_task.macro_task',
    #     'schedule':20,
    #     'args':("0x5C30940A4544cA845272FE97c4A27F2ED2CD7B64",)
    # },

    'User_trasaction':{
        'task':'tasks.agent_tasks.onchain_task.transaction_task',
        'schedule':60,
    }
    
}

# celery_app.autodiscover_tasks(['tasks'])
