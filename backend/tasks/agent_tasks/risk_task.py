from core import celery_app

@celery_app.task
def risk_task()->bool:
    print('Running risk task...')
    return {'risk_task':'started'}