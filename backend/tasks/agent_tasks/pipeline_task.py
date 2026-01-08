import asyncio

from data_pipeline.pipeline import Pipeline
from celery import shared_task
from core import celery_app


pipeline = Pipeline()

"""
scheduler:
    pipeline task are run on schedule
    The end output are stored in the database for easy acccess by the API
"""

@shared_task
def test():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    pipline = loop.run_until_complete(
        pipeline.test_pipe()
    )


@shared_task
def mantle_protocols():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    pipline = loop.run_until_complete(
        pipeline.mantle_protocols()
    )

@shared_task
def mantle_yield():
    print('starting Mantle yield')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    pipline = loop.run_until_complete(
        pipeline.mantle_yield()
    )
    # pipeline.mantle_yield()

@celery_app.task
def user_portfolio(wallet_address:str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    portfolio_data = loop.run_until_complete(
        pipeline.user_portfolio(wallet_address)
    )
    return portfolio_data

@celery_app.task
def user_token_balance(token_address:str,wallet_address:str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    user_token_balance_data = loop.run_until_complete(
        pipeline.user_token_balance(token_address,wallet_address)
    )
