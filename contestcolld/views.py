#!/usr/bin/python
# coding: utf-8

from contestcolld import app

message = app.config['HELLO_WORLD']

@app.route('/')
def webapp():
    return message
