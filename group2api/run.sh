#!/bin/bash
export FLASK_APP=app.py
export FLASK_DEBUG=1
source setenvvar.sh
flask run --host=0.0.0.0
