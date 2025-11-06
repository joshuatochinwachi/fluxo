from core import celery_app

@celery_app.task
def social_task()->bool:
    print('Running social task...')
    return {'social_task':'started'}