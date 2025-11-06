from core import celery_app

@celery_app.task
def macro_task()->bool:
    print('Running macro task...')
    return {'macro_task':'started'}