#!/bin/sh

./bin/python/bin/gunicorn \
    --access-logfile=log/gunicorn_access.log \
    --error-logfile=log/gunicorn_error.log \
    -w 4 -b frontend:8080 run_frontend:app
