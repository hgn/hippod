#!/usr/bin/python
# coding: utf-8

from contestcolld import app

from flask import render_template


@app.route('/admin')
def page_admin():
    css_includes     = ['css/bootstrap.min.css', 'css/styles.css']
    js_body_includes = []
    js_head_includes = [ 'js/jquery.min.js', 'js/bootstrap.min.js', 'js/admin-main.js']
    return render_template('admin.html', title='Home',
            css_includes=css_includes,
            js_body_includes=js_body_includes,
            js_head_includes=js_head_includes)
