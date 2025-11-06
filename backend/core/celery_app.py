from celery import Celery

celery_app = Celery(
    "Backend-Worker",
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
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
    ]
)