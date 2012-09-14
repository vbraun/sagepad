
from celery import Celery
from celery.signals import worker_process_init
import celery_config

from evaluate import evaluate_command, evaluate_command_pipe
from sage_session import SageSession

celery = Celery('SagePad')
celery.config_from_object(celery_config)


############################################################3

@celery.task
def add(x, y):
    return x + y

############################################################3

@celery.task
def evaluate_gap(pad_input):
    return evaluate_command_pipe(['sage', '-gap'], '.gap', pad_input)

@celery.task
def evaluate_singular(pad_input):
    return evaluate_command(['sage', '-singular', '-b'], '.singular', pad_input)

@celery.task
def evaluate_bash(pad_input):
    return evaluate_command(['bash'], '.sh', pad_input)


############################################################3

sage_instance = None

@worker_process_init.connect 
def worker_process_init_handler(**kwargs): 
    print('worker_process_init '+str(kwargs))
    global sage_instance
    sage_instance = SageSession()

@celery.task
def evaluate_sage(pad_input):
    global sage_instance
    print('evaluate_sage prev='+str(sage_instance))
    result = sage_instance.eval_dict(pad_input)
    sage_instance.close()
    sage_instance = SageSession()
    return result

    #return evaluate_command(['sage'], '.sage', pad_input)
