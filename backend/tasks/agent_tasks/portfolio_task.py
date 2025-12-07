import asyncio
from typing import List
from core import celery_app

# @celery_app.task
# def portfolio_task()->bool:
#     print('Running portfolio task...')
#     return {'portfolio_task':'started'}


@celery_app.task
def portfolio_task()->None:
    print('Fetching User Portfolio')

    # import to avoid circular import erro
    from agents.portfolio_agent import portfolio_agent

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    portfolio = portfolio_agent()
    loop.run_until_complete(
        portfolio.analyze_portfolio()
    )