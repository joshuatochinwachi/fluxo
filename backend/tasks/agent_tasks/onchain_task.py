from core import celery_app

@celery_app.task
def onchain_task()->bool:
    print('Running ochain task...')
    return {'Onchain_task':'started'}

