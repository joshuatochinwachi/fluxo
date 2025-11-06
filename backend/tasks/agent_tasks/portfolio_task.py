from core import celery_app

@celery_app.task
def portfolio_task()->bool:
    print('Running portfolio task...')
    return {'portfolio_task':'started'}