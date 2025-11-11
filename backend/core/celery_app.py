from celery import Celery
from .config import Settings

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