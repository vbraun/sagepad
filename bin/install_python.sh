#!/bin/sh


if [ ! -x "run_frontend.py" ] ; then
    echo "Script needs to be run in the main directory (the one contaninig run_frontend.py)."
    exit 1
fi


virtdir="bin/python"

virtualenv "$virtdir"
"$virtdir"/bin/pip install --upgrade celery pymongo flask-openid ipython gunicorn


