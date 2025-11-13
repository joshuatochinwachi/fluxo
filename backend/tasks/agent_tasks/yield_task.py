import asyncio
from core import celery_app

@celery_app.task
def yield_task()->bool:
    print('Running yield task...')

    # import to avoid circular import error (lazy import)
    from agents.yield_agent import yield_agent

    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield_protocol = yield_agent()
    yield_protocol_data = loop.run_until_complete(
        yield_protocol.yield_opportunity()
    )

    return yield_protocol_data