from core import celery_app

@celery_app.task
def market_data_task()->bool:
    print('Running market_data task...')
    return {'market_data_task':'started'}