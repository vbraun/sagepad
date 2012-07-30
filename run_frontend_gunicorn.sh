#!/bin/sh

./bin/python/bin/gunicorn -w 4 -b frontend:8080 run_frontend:app
