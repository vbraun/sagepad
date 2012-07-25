from celery import Celery
import celery_config

from evaluate import evaluate_command



#celery = Celery('SagePad', 
#                backend=celery_config.BROKER_TRANSPORT, 
#                broker=celery_config.BROKER_URL)

celery = Celery('SagePad')
celery.config_from_object(celery_config)

@celery.task
def add(x, y):
    return x + y


@celery.task
def evaluate_sage(pad_input):
    return evaluate_command(['sage'], '.sage', pad_input)
