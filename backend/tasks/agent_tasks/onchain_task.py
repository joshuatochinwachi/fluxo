import asyncio
from typing import List

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







