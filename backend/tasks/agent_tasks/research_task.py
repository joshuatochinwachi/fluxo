from core import celery_app

@celery_app.task
def research_task()->bool:
    print('Running research task...')
    return {'research_task':'started'}