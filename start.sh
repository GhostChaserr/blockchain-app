#!/bin/sh
export LC_ALL=C.UTF-8 && export LANG=C.UTF-8 
export APP_NAME='BLOCKCHAIN'
uvicorn main:app --host 0.0.0.0 --port 5200 --workers=3 --reload