from core import celery_app

@celery_app.task
def yield_task()->bool:
    print('Running yield task...')
    return {'yield_task':'started'}