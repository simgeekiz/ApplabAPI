#!/bin/bash
export FLASK_APP=app.py
export FLASK_DEBUG=1
bash setenvvar.sh
flask run
