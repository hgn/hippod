#!/usr/bin/python
# coding: utf-8

from contestcolld import app

from flask import render_template

message = app.config['HELLO_WORLD']

@app.route('/')
def webapp():
    user = {'nickname': 'Miguel'}
    css_includes     = ['css/bootstrap.min.css', 'css/styles.css']
    js_body_includes = []
    js_head_includes = [ 'js/jquery.min.js', 'js/bootstrap.min.js', 'js/scripts.js']
    return render_template('index.html', title='Home', user=user,
            css_includes=css_includes,
            js_body_includes=js_body_includes,
            js_head_includes=js_head_includes)

@app.route('/overview')
def tests():
    user = {'nickname': 'Miguel'}
    css_includes     = ['css/bootstrap.min.css', 'css/styles.css']
    js_body_includes = []
    js_head_includes = [ 'js/jquery.min.js', 'js/bootstrap.min.js', 'js/scripts.js']
    return render_template('overview.html', title='Home', user=user,
            css_includes=css_includes,
            js_body_includes=js_body_includes,
            js_head_includes=js_head_includes)
