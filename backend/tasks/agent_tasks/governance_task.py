from core import celery_app

@celery_app.task
def governance_task()->bool:
    print('Running governance task...')
    return {'governance_task':'started'}