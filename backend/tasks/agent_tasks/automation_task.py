from core import celery_app

@celery_app.task
def automation_task()->bool:
    print('Running automation task...')
    return {'automation_task':'started'}