from core import celery_app

@celery_app.task
def x402_task()->bool:
    print('Running x402 task...')
    return {'x402_task':'started'}