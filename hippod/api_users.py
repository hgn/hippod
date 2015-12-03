#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import hippod.hasher
import hippod.ex3000
import hippod.users

from hippod.error_object import *

from hippod import app

from flask import jsonify
from flask import request


def get_user_data(req_obj):
    if not 'filter' in req_obj:
        msg = "user data MUST contain a filter"
        raise ApiError(msg)
    user_filter = req_obj['filter']
    return hippod.users.get(user_filter=user_filter)


@app.route('/api/v1/users', methods=['GET', 'POST'])
def get_users():
    try:
        start = time.clock()
        req_obj = request.get_json(force=False)
        data = get_user_data(req_obj)
        end = time.clock()
    except ApiError as e:
        return e.transform()

    o = hippod.ex3000.Ex3000()
    o['data'] = data
    o['processing-time'] = "{0:.4f}".format(end - start)
    return o.transform()

