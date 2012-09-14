#!./bin/python/bin/python

import os, sys
sys.path.append('src')
sys.path.append('secure')

#from sagepad.backend.configure import configure_celery
#configure_celery(os.path.join(os.getcwd(), 'secure', 'celery_config.py'))

from sagepad.backend.tasks import add, evaluate_sage, evaluate_gap, evaluate_singular, evaluate_bash


import random
a = random.randrange(0,10)
b = random.randrange(0,10)
print ''.join([str(a), '+', str(b),' = ', str(add.delay(a,b).get())])

print evaluate_bash.delay('ls -alZt').get()

print ''.join([str(a), '+', str(b),' = ', str(evaluate_gap.delay(str(a)+'+'+str(b)+';').get())])
print ''.join([str(a), '+', str(b),' = ', str(evaluate_singular.delay(str(a)+'+'+str(b)+';').get())])
print ''.join([str(a), '+', str(b),' = ', str(evaluate_sage.delay(str(a)+'+'+str(b)).get())])
