import asyncio
from typing import List

from celery import shared_task
from core import celery_app

@celery_app.task
def onchain_task()->bool:
    print('Running ochain task...')
    return {'Onchain_task':'started'}



@celery_app.task
def protocol_task()->bool:
    """
        fetch Mantle protocol from onchain agent
    """
    print('Running protocol task...')
    from agents.onchain_agent import onchain_agent

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    protocol = onchain_agent()
    protocol_data = loop.run_until_complete(
        protocol.protocols()
    )

    return protocol_data

@shared_task
def transaction_task()->None:
    """
        Fetch User Transactions and Update to db
    """
    from agents.onchain_agent import onchain_agent

    onchain_agent = onchain_agent()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(
        onchain_agent.fetch_transaction_and_update_db()
    )

@celery_app.task
def fetch_transaction(wallet_address)->list:
    """
    Fetch User Transaction from db
    """
    from agents.onchain_agent import onchain_agent
    agent =  onchain_agent()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    transaction = loop.run_until_complete(
        agent.retrieve_transcton_from_db(wallet_address)
    )
    return transaction






