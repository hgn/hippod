#!/usr/bin/python
# coding: utf-8

from hippod import app

from flask import render_template

message = app.config['HELLO_WORLD']

@app.route('/')
def webapp():
    return app.send_static_file('index.html')
