#!/usr/bin/python
# coding: utf-8

from hippod import app

from flask import render_template

@app.route('/items')
def items():
    css_includes     = ['css/bootstrap.min.css', 'css/styles.css' ]
    js_body_includes = []
    js_head_includes = [ 'js/jquery.min.js', 'js/bootstrap.min.js', 'js/items-main.js']
    return render_template('items.html',
            css_includes=css_includes,
            js_body_includes=js_body_includes,
            js_head_includes=js_head_includes)
