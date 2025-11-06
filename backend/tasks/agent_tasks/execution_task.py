from core import celery_app

@celery_app.task
def execution_task()->bool:
    print('Running execution task...')
    return {'execution_task':'started'}