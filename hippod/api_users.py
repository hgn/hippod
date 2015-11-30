#!/usr/bin/python
# coding: utf-8

import json
import os
import datetime
import time
import sys

import hippod.hasher
import hippod.api_comm
import hippod.users

from hippod.api_err_obj import *

from hippod import app

from flask import jsonify
from flask import request


def get_user_data():
    return hippod.users.get()


@app.route('/api/v1/users', methods=['GET'])
def get_users():
    try:
        start = time.clock()
        data = get_user_data()
        end = time.clock()
    except ApiError as e:
        return e.transform()
    #except Exception as e:
    #    return ApiError(str(e), 200).transform()

    o = hippod.api_comm.Dict3000()
    o['data'] = data
    o.http_code(202)
    return o.transform()

