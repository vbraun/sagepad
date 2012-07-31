#!/bin/sh

./bin/python/bin/gunicorn --access-logfile=- --error-logfile=- -w 4 -b frontend:8080 run_frontend:app
