BROKER_URL = 'amqp://frontend:5672//'

CELERY_RESULT_BACKEND = "amqp"
CELERY_TASK_RESULT_EXPIRES = 1800 # 30 mins
CELERY_TASK_SERIALIZER='json'



